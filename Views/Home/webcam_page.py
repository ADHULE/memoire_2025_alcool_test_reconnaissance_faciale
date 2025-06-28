# Suppression de `import os` (inutile)
import cv2
import numpy as np
import datetime
from insightface.app import FaceAnalysis

from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *

from Controllers.chauffeur_controller import CHAUFFEUR_CONTROLLER
from Controllers.image_controller import IMAGE_CONTROLLER


class ACCER_WEBCAMERA(QMainWindow):
    mainwindow_signal = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("GESTION DE LA RECONNAISSANCE FACIALE")

        self.face_engine = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
        self.face_engine.prepare(ctx_id=0)

        self.face_db = []
        self.recognition_threshold = 0.65
        self.cap = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_frame)

        self.saved_urls = []
        self.active_url = None
        self.fullscreen = False

        self.person_controller = CHAUFFEUR_CONTROLLER()
        self.image_controller = IMAGE_CONTROLLER()

        self._setup_ui()
        self._load_face_database()

    def _setup_ui(self):
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        self.label_video = QLabel("Flux vidéo")
        self.label_video.setAlignment(Qt.AlignCenter)
        self.label_video.setScaledContents(True)
        layout.addWidget(self.label_video)

        controls = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("URL de la caméra IP (ex: rtsp://...)")
        controls.addWidget(self.url_input)

        self.connect_url_button = QPushButton("Activer URL")
        self.connect_url_button.clicked.connect(self._handle_url_connection)
        controls.addWidget(self.connect_url_button)

        self.cam_selector = QComboBox()
        self.cam_selector.addItems(self._detect_local_cameras())
        controls.addWidget(self.cam_selector)

        self.connect_local_button = QPushButton("Activer Webcam")
        self.connect_local_button.clicked.connect(self._start_local_camera)
        controls.addWidget(self.connect_local_button)

        self.stop_button = QPushButton("Arrêter")
        self.stop_button.clicked.connect(self._stop_camera)
        controls.addWidget(self.stop_button)

        self.fullscreen_button = QPushButton("Plein écran")
        self.fullscreen_button.clicked.connect(self._toggle_fullscreen)
        controls.addWidget(self.fullscreen_button)

        layout.addLayout(controls)
        self.setCentralWidget(central_widget)

    def _detect_local_cameras(self):
        available = []
        for index in range(5):
            cap = cv2.VideoCapture(index)
            if cap.read()[0]:
                available.append(f"Caméra {index}")
                cap.release()
        return available or ["Aucune caméra détectée"]

    def _handle_url_connection(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Erreur", "Veuillez entrer une URL valide.")
            return
        self.saved_urls.append(url)
        self._open_camera(url)
        self.url_input.setText("Connecté")

    def _start_local_camera(self):
        try:
            index = int(self.cam_selector.currentText().split()[-1])
            self._open_camera(index)
        except Exception:
            QMessageBox.warning(self, "Erreur", "Sélection de caméra invalide.")

    def _open_camera(self, source):
        self._stop_camera()
        self.cap = cv2.VideoCapture(source)
        if self.cap.isOpened():
            self.timer.start(30)
            if isinstance(source, str):
                self.active_url = source
        else:
            QMessageBox.critical(self, "Erreur", "Impossible d’accéder à la caméra.")

    def _stop_camera(self):
        self.timer.stop()
        if self.cap:
            self.cap.release()
        self.cap = None
        self.label_video.clear()
        self.url_input.setText("")

    def _toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.showFullScreen()
            self.fullscreen_button.setText("Quitter plein écran")
        else:
            self.showNormal()
            self.fullscreen_button.setText("Plein écran")

    def _load_face_database(self):
        self.face_db.clear()
        try:
            self.all_photos = self.image_controller.get_all_photos()
            person = self.person_controller.get_driver_by_id(self.all_photos.personne_id)
        except Exception as e:
            print("Erreur de chargement des chauffeurs :", e)
            return

        for chauf in person:
            try:
                # photo_data = self.image_controller.get_photo(chauf.id)
                # if not photo_data:
                #     continue
                img = cv2.imread("systeme_adhule.jpeg")

                if img is None:
                    continue
                faces = self.face_engine.get(img)
                if not faces:
                    continue
                self.face_db.append({
                    "nom": f"{chauf.nom} {chauf.prenom} | Tel: {chauf.telephone} | Email: {chauf.email} | Permis: {chauf.numero_permis} | Sexe: {chauf.sex}",
                    "embedding": faces[0].embedding,
                    "fonction": getattr(chauf, "fonction", None),
                    "id": getattr(chauf, "id", None)
                })
            except Exception as e:
                print(f"Erreur de traitement photo ({chauf.nom}): {e}")

    def _log_recognition(self, name, score):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("reconnaissance_log.txt", "a") as f:
            f.write(f"[{timestamp}] {name} - Score : {score:.4f}\n")

    def _update_frame(self):
        if not self.cap or not self.cap.isOpened():
            return
        ret, frame = self.cap.read()
        if not ret:
            return
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        faces = self.face_engine.get(rgb_frame)

        for face in faces:
            bbox = face.bbox.astype(int)
            cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 2)

            name = "Inconnu"
            best_score = 0.0

            for profile in self.face_db:
                sim = np.dot(face.embedding, profile["embedding"]) / (
                    np.linalg.norm(face.embedding) * np.linalg.norm(profile["embedding"])
                )
                if sim > self.recognition_threshold and sim > best_score:
                    name = profile["nom"]
                    best_score = sim

            cv2.putText(frame, name, (bbox[0], bbox[1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

            if name != "Inconnu":
                self._log_recognition(name, best_score)

        h, w, ch = frame.shape
        qimg = QImage(frame.data, w, h, ch * w, QImage.Format_BGR888)
        self.label_video.setPixmap(QPixmap.fromImage(qimg))
