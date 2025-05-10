import os
import cv2
import numpy as np

from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *

from Controllers.chauffeur_controller import CHAUFFEUR_CONTROLLER

# Chargement du détecteur de visages avec meilleurs paramètres
facedetec = cv2.CascadeClassifier("Views/image/haarcascade_frontalface_default.xml")

# Vérification du module de reconnaissance faciale
if not hasattr(cv2, "face"):
    raise ImportError("Le module 'cv2.face' n'est pas disponible. Installez 'opencv-contrib-python'.")

# Initialisation du modèle LBPH avec paramètres optimisés
recognizer = cv2.face.LBPHFaceRecognizer_create()
if os.path.exists("captured_faces/training_data.yml"):
    recognizer.read("captured_faces/training_data.yml")
else:
    print("⚠️ Fichier de données d'entraînement manquant!")

class FaceRecognitionApp(QWidget):
    """Application améliorée de reconnaissance faciale."""
    login_page_signal = Signal()
    mainwindow_signal = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Reconnaissance Faciale")
        self.camera = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_frame)
        self.is_fullscreen = False
        self._setup_ui()

    def _create_button(self, text, callback, enabled=True):
        button = QPushButton(text)
        button.clicked.connect(callback)
        button.setEnabled(enabled)
        return button

    def _setup_ui(self):
        """Amélioration de l'interface utilisateur."""
        main_layout = QHBoxLayout(self)
        self.video_label = QLabel("Vidéo")
        self.video_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.video_label, 1)

        button_widget = QWidget()
        button_layout = QVBoxLayout(button_widget)
        button_layout.setAlignment(Qt.AlignTop)

        self.start_button = self._create_button("Démarrer", self._start_camera)
        self.stop_button = self._create_button("Arrêter", self._stop_camera, False)
        self.fullscreen_button = self._create_button("Plein Écran", self._toggle_fullscreen)

        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.fullscreen_button)
        button_layout.addStretch(1) 

        main_layout.addWidget(button_widget)

    def _start_camera(self):
        self.camera = cv2.VideoCapture(0)
        if not self.camera.isOpened():
            QMessageBox.critical(self, "Erreur", "Impossible d'ouvrir la caméra.")
            return
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.timer.start(30)

    def _stop_camera(self):
        if self.camera and self.camera.isOpened():
            self.timer.stop()
            self.camera.release()
            self.video_label.clear()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def _update_frame(self):
        if self.camera and self.camera.isOpened():
            ret, frame = self.camera.read()
            if ret:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = facedetec.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=7)  # Paramètres améliorés
                self._recognize_faces(frame, gray, faces)
                self._display_frame(frame)
            else:
                QMessageBox.warning(self, "Erreur", "Erreur lors de la capture.")
                self._stop_camera()

    def _recognize_faces(self, frame, gray, faces):
        """Reconnaît les visages détectés et améliore la précision."""
        for x, y, w, h in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cropped_face = gray[y:y + h, x:x + w]
            personne_id_predit, confidence = recognizer.predict(cropped_face)
            if confidence < 80:  # Seuil de confiance ajusté
                personne_info = self._get_personne_info(personne_id_predit)
                self._draw_annotations(frame, personne_info, x, y)
            else:
                cv2.putText(frame, "Visage inconnu", (x, y - 10), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255), 2)

    def _get_personne_info(self, personne_id):
        chauffeur_controller = CHAUFFEUR_CONTROLLER()
        return chauffeur_controller.get_driver_by_id(personne_id)

    def _draw_annotations(self, frame, personne_info, x, y):
        if personne_info and hasattr(personne_info, "nom"):
            nom = f"{personne_info.nom} {personne_info.postnom or ''}"
            telephone = personne_info.telephone or ""
            cv2.putText(frame, f"Nom: {nom}", (x, y - 25), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 255, 127), 2)
            cv2.putText(frame, f"Téléphone: {telephone}", (x, y - 50), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 255, 127), 2)

    def _display_frame(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        q_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image).scaled(self.video_label.size(), Qt.KeepAspectRatio)
        self.video_label.setPixmap(pixmap)

    def _toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        self.showFullScreen() if self.is_fullscreen else self.showNormal()
