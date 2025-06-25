import os
import cv2
import numpy as np
import datetime
from PySide6.QtWidgets import *
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt, QTimer, Signal
from insightface.app import FaceAnalysis

class ACCER_WEBCAMERA(QMainWindow):
    mainwindow_signal = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Reconnaissance Faciale avec InsightFace")

        self.face_engine = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
        self.face_engine.prepare(ctx_id=0)

        self.face_db = []
        self.recognition_threshold = 0.65
        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_frame)
        self.fullscreen = False

        self._setup_ui()
        self._load_face_database("photos_db")

    def _setup_ui(self):
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        self.label_video = QLabel("Flux vidéo")
        self.label_video.setAlignment(Qt.AlignCenter)
        self.label_video.setScaledContents(True)
        layout.addWidget(self.label_video)

        config_layout = QHBoxLayout()

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("URL de la caméra IP (ex: rtsp://...)")
        config_layout.addWidget(self.url_input)

        self.connect_url_button = QPushButton("Activer URL")
        self.connect_url_button.clicked.connect(self._start_url_camera)
        config_layout.addWidget(self.connect_url_button)

        self.cam_selector = QComboBox()
        self.cam_selector.addItems(self._detect_local_cameras())
        config_layout.addWidget(self.cam_selector)

        self.connect_local_button = QPushButton("Activer Webcam")
        self.connect_local_button.clicked.connect(self._start_local_camera)
        config_layout.addWidget(self.connect_local_button)

        self.stop_button = QPushButton("Arrêter")
        self.stop_button.clicked.connect(self._stop_camera)
        config_layout.addWidget(self.stop_button)

        self.fullscreen_button = QPushButton("Plein écran")
        self.fullscreen_button.clicked.connect(self._toggle_fullscreen)
        config_layout.addWidget(self.fullscreen_button)

        layout.addLayout(config_layout)
        self.setCentralWidget(central_widget)

    def _load_face_database(self, folder_path):
        if not os.path.exists(folder_path):
            return
        for filename in os.listdir(folder_path):
            if filename.lower().endswith((".jpg", ".jpeg", ".png")):
                path = os.path.join(folder_path, filename)
                img = cv2.imread(path)
                faces = self.face_engine.get(img)
                if faces:
                    name = os.path.splitext(filename)[0]
                    self.face_db.append({
                        "nom": name,
                        "embedding": faces[0].embedding
                    })

    def _detect_local_cameras(self):
        available = []
        for index in range(5):
            cap = cv2.VideoCapture(index)
            if cap.read()[0]:
                available.append(f"Caméra {index}")
                cap.release()
        return available or ["Aucune caméra détectée"]

    def _start_local_camera(self):
        index = int(self.cam_selector.currentText().split()[-1])
        self._open_camera(index)

    def _start_url_camera(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Erreur", "Veuillez entrer une URL valide.")
            return
        self._open_camera(url)

    def _open_camera(self, source):
        self._stop_camera()
        self.cap = cv2.VideoCapture(source)
        if self.cap.isOpened():
            self.timer.start(30)
        else:
            QMessageBox.critical(self, "Erreur", "Impossible d’accéder à la caméra.")

    def _stop_camera(self):
        self.timer.stop()
        if self.cap and self.cap.isOpened():
            self.cap.release()
        self.label_video.clear()

    def _toggle_fullscreen(self):
        if self.fullscreen:
            self.showNormal()
            self.fullscreen = False
            self.fullscreen_button.setText("Plein écran")
        else:
            self.showFullScreen()
            self.fullscreen = True
            self.fullscreen_button.setText("Quitter plein écran")

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

            label = f"{name} ({int(face.age)} ans)" if hasattr(face, "age") else name
            cv2.putText(frame, label, (bbox[0], bbox[1]-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

            if name != "Inconnu":
                self._log_recognition(name, best_score)

        h, w, ch = frame.shape
        qimg = QImage(frame.data, w, h, ch * w, QImage.Format_BGR888)
        self.label_video.setPixmap(QPixmap.fromImage(qimg))
