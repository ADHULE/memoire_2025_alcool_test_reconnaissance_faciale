import os
import cv2
import numpy as np
import face_recognition  # Bibliothèque avancée pour la reconnaissance faciale
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *

from Controllers.chauffeur_controller import CHAUFFEUR_CONTROLLER
from Controllers.image_controller import IMAGE_CONTROLLER

class FaceRecognitionApp(QWidget):
    """Application utilisant uniquement FaceRecognition pour la reconnaissance faciale."""
    login_page_signal = Signal()
    mainwindow_signal = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Reconnaissance Faciale (FaceRecognition Uniquement)")
        self.camera = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_frame)
        self.is_fullscreen = False
        self._known_face_encodings = []
        self._known_face_names = []

        # initialisation des objets des classes
        self.image_controller = IMAGE_CONTROLLER()
        self.chauffeur_controller = CHAUFFEUR_CONTROLLER() # Nom de variable corrigé

        self._load_known_faces_from_database() # Charge les visages connus depuis la base de données
        self._setup_ui()

    def _load_known_faces_from_database(self):
        """Charge les encodages des visages connus en utilisant les photos de la base de données."""
        known_faces_data = self.image_controller.get_all_photos()
        if not known_faces_data:
            print("⚠️ Aucune photo disponible dans la base de données pour charger les visages connus.")
            return

        for photo in known_faces_data:
            try:
                image_path = photo.url
                image = face_recognition.load_image_file(image_path)
                encodings = face_recognition.face_encodings(image)
                person_info = self.chauffeur_controller.get_driver_by_id(photo.personne_id)
                name = "Inconnu"
                if person_info:
                    name = f"{person_info.nom} {person_info.prenom}"

                if encodings:
                    self._known_face_encodings.append(encodings[0])
                    self._known_face_names.append(name)
                else:
                    print(f"⚠️ Aucun visage détecté dans l'image: {image_path}")
            except Exception as e:
                print(f"⚠️ Erreur lors du chargement de l'image {photo.url}: {e}")

        if self._known_face_names:
            print(f"✅ {len(self._known_face_names)} visages connus chargés depuis la base de données.")
        else:
            print("⚠️ Aucun visage connu n'a été chargé depuis la base de données.")

    def _create_button(self, text, callback, enabled=True):
        """Crée un bouton avec texte et action."""
        button = QPushButton(text)
        button.clicked.connect(callback)
        button.setEnabled(enabled)
        return button

    def _setup_ui(self):
        """Configure l'interface utilisateur."""
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
        self.setLayout(main_layout)

    def _start_camera(self):
        """Démarre la caméra et active la reconnaissance."""
        self.camera = cv2.VideoCapture(0)
        if not self.camera.isOpened():
            QMessageBox.critical(self, "Erreur", "Impossible d'ouvrir la caméra.")
            return
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.timer.start(30)

    def _stop_camera(self):
        """Arrête la caméra proprement."""
        if self.camera and self.camera.isOpened():
            self.timer.stop()
            self.camera.release()
            self.video_label.clear()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def _update_frame(self):
        """Capture et analyse chaque frame vidéo."""
        if self.camera and self.camera.isOpened():
            ret, frame = self.camera.read()
            if not ret or frame is None:
                print("⚠️ Erreur de capture d'image.")
                self._stop_camera()
                return

            # 🔹 Conversion BGR → RGB pour FaceRecognition
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # 🔹 Reconnaissance des visages avec FaceRecognition
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            for face_encoding, face_location in zip(face_encodings, face_locations):
                # 🔹 Comparaison avec les visages connus
                matches = face_recognition.compare_faces(self._known_face_encodings, face_encoding)
                name = "Inconnu"

                if True in matches:
                    first_match_index = matches.index(True)
                    name = self._known_face_names[first_match_index]

                # 🔹 Dessine un rectangle et affiche le nom
                top, right, bottom, left = face_location
                cv2.rectangle(rgb_frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(rgb_frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

            self._display_frame(frame, rgb_frame) # Passe le frame original et le frame RGB annoté

    def _display_frame(self, bgr_frame, rgb_frame_annotated):
        """Affiche la frame avec annotations et détections."""
        h, w, ch = rgb_frame_annotated.shape
        bytes_per_line = ch * w
        q_image = QImage(rgb_frame_annotated.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image).scaled(self.video_label.size(), Qt.KeepAspectRatio)
        self.video_label.setPixmap(pixmap)

    def _toggle_fullscreen(self):
        """Active/désactive le mode plein écran."""
        self.is_fullscreen = not self.is_fullscreen
        self.showFullScreen() if self.is_fullscreen else self.showNormal()

