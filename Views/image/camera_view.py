from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QMessageBox, QFileDialog, QSpinBox
)
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt, QTimer, Signal
import cv2
import os
import datetime

class CameraView(QWidget):
    """Interface pour la capture d'images de visage avec options de configuration de caméra."""

    image_captured_signal = Signal(str)
    finished = Signal(str)

    def __init__(self, parent=None, identifier=None):
        super().__init__(parent)
        self.setWindowTitle("Configuration Caméra et Capture Visage")
        self.identifier = identifier
        self.capture, self.current_frame = None, None
        self.is_capturing, self.is_fullscreen = False, False
        self.output_directory = "captured_faces"
        self.target_size = (300, 400)


        # Compteur de photos pour l'enregistrement automatique
        self.photo_count_to_capture = 1
        self.photos_captured_current_session = 0
        self.is_recording_faces = False

        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)

        self._setup_ui()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_frame)
        self.load_stylesheet("Styles/webcam_style.css")

    def _setup_ui(self):
        """Configure l'interface utilisateur."""
        main_layout = QHBoxLayout(self)

        # Zone d'affichage vidéo
        self.video_label = self._create_label(alignment=Qt.AlignCenter)
        main_layout.addWidget(self.video_label, 1)

        # Zone de contrôles
        self.controls_widget = QWidget()
        self.controls_layout = QVBoxLayout(self.controls_widget)

        # Sous-layout pour l'ajout d'URL de caméra IP
        self.url_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Entrer l'URL de la caméra IP")
        self.add_url_button = self._create_button("Ajouter URL", self.start_camera)
        self.url_layout.addWidget(self.url_input)
        self.url_layout.addWidget(self.add_url_button)
        self.controls_layout.addLayout(self.url_layout)

        # Bouton pour la caméra par défaut
        self.default_camera_button = self._create_button("Caméra par Défaut", self.start_default_camera)
        self.controls_layout.addWidget(self.default_camera_button)

        # Boutons de contrôle de la caméra
        self.start_button = self._create_button("Ouvrir Caméra (Indice 0)", lambda: self._open_camera(0), enabled=True)
        self.stop_button = self._create_button("Fermer Caméra", self._stop_camera, enabled=False)

        # Champs pour le nombre de photos à capturer automatiquement
        self.photo_count_layout = QHBoxLayout()
        self.photo_count_label = QLabel("Photos à capturer:")
        self.photo_count_input = QSpinBox()
        self.photo_count_input.setMinimum(1)
        self.photo_count_input.setMaximum(100)
        self.photo_count_input.setValue(1)
        self.photo_count_input.valueChanged.connect(self._update_photo_count)
        self.photo_count_layout.addWidget(self.photo_count_label)
        self.photo_count_layout.addWidget(self.photo_count_input)
        self.controls_layout.addLayout(self.photo_count_layout)

        # Boutons d'enregistrement automatique
        self.start_recording_button = self._create_button("Démarrer Enregistrement Auto", self._start_automatic_face_capture, enabled=False)
        self.stop_recording_button = self._create_button("Arrêter Enregistrement Auto", self._stop_automatic_face_capture, enabled=False)

        # Autres contrôles
        self.fullscreen_button = self._create_button("Plein Écran", self._toggle_fullscreen)
        self.change_dir_button = self._create_button("Changer Répertoire", self._change_output_directory)

        # Ajout des boutons au layout des contrôles
        self.controls_layout.addWidget(self.start_button)
        self.controls_layout.addWidget(self.stop_button)
        self.controls_layout.addWidget(self.start_recording_button)
        self.controls_layout.addWidget(self.stop_recording_button)
        self.controls_layout.addWidget(self.fullscreen_button)
        self.controls_layout.addWidget(self.change_dir_button)
        self.controls_layout.addStretch(1) # Espace flexible pour pousser les éléments vers le haut

        main_layout.addWidget(self.controls_widget, 0)
        self.setLayout(main_layout)

    def set_chauffeur_id(self, chauffeur_id):
        """Définit l'identifiant du chauffeur associé à la capture."""
        self.identifier = chauffeur_id

    def _create_label(self, alignment=None):
        """Crée un QLabel avec un alignement optionnel."""
        label = QLabel()
        if alignment:
            label.setAlignment(alignment)
        return label

    def _create_button(self, text, callback, enabled=True):
        """Crée un QPushButton avec un texte, un callback et un état d'activation."""
        button = QPushButton(text)
        button.clicked.connect(callback)
        button.setEnabled(enabled)
        return button

    def start_default_camera(self):
        """Démarre la capture vidéo depuis la caméra par défaut (indice 0)."""
        self._open_camera(0)

    def start_camera(self):
        """Démarre la capture vidéo depuis une URL de caméra IP."""
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Avertissement", "Veuillez entrer l'URL de la caméra.")
            return
        self._open_camera(url)

    def _open_camera(self, camera_source):
        """Ouvre la caméra spécifiée par la source (indice ou URL)."""
        if self.capture and self.capture.isOpened():
            self._stop_camera()

        self.capture = cv2.VideoCapture(camera_source)

        if not self.capture.isOpened():
            QMessageBox.critical(self, "Erreur", f"Impossible d'ouvrir la caméra : {camera_source}")
            self.capture = None
            self.video_label.clear()
            self.is_capturing = False
            self._toggle_buttons(start=True, stop=False, start_record=False, stop_record=False)
            return

        QMessageBox.information(self, "Info", f"Caméra connectée à : {camera_source}")
        if isinstance(camera_source, str):
            self.url_input.clear()
        self.is_capturing = True
        self.timer.start(30) # Met à jour le flux vidéo toutes les 30ms
        self._toggle_buttons(start=False, stop=True, start_record=True, stop_record=False)
        self.photos_captured_current_session = 0
        self.is_recording_faces = False

    def _stop_camera(self):
        """Arrête la capture vidéo et libère les ressources."""
        if self.is_capturing and self.capture and self.capture.isOpened():
            self.timer.stop()
            self.capture.release()
            self.capture = None
            self.is_capturing = False
            self.video_label.clear()
            self._toggle_buttons(start=True, stop=False, start_record=False, stop_record=False)
            self.photos_captured_current_session = 0
            self.is_recording_faces = False

    def _update_frame(self):
        """Met à jour l'affichage vidéo en direct et gère la détection/capture de visages."""
        if self.is_capturing and self.capture and self.capture.isOpened():
            ret, frame = self.capture.read()
            if ret:
                self.current_frame = frame
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(30, 30))

                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_frame.shape
                bytes_per_line = ch * w
                q_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(q_image).scaled(self.video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.video_label.setPixmap(pixmap)

                # Logique d'enregistrement automatique des visages
                if self.is_recording_faces and self.photos_captured_current_session < self.photo_count_to_capture:
                    if len(faces) > 0:
                        (x, y, w, h) = faces[0] # Prend le premier visage détecté
                        face_roi_gray = gray[y:y + h, x:x + w]
                        resized_face_gray = cv2.resize(face_roi_gray, self.target_size)

                        filename = (f"{self.identifier}_face_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_"
                                    f"{self.photos_captured_current_session + 1}.png"
                                    if self.identifier else
                                    f"face_capture_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_"
                                    f"{self.photos_captured_current_session + 1}.png")

                        filepath = os.path.join(self.output_directory, filename)
                        cv2.imwrite(filepath, resized_face_gray)

                        self.photos_captured_current_session += 1
                        QMessageBox.information(self, "Capture Automatique",
                                                f"Visage {self.photos_captured_current_session}/"
                                                f"{self.photo_count_to_capture} enregistré sous : {filepath}")
                        self.image_captured_signal.emit(filepath)

                        if self.photos_captured_current_session >= self.photo_count_to_capture:
                            self._stop_automatic_face_capture()
                            QMessageBox.information(self, "Enregistrement Terminé",
                                                    f"Toutes les {self.photo_count_to_capture} photos ont été capturées automatiquement.")
                            self.finished.emit("Automatic multiple captures completed.")
            else:
                self._stop_camera()
                QMessageBox.warning(self, "Avertissement", "Flux vidéo terminé ou interrompu.")

    def _update_photo_count(self, value):
        """Met à jour le nombre de photos à capturer automatiquement."""
        self.photo_count_to_capture = value

    def _start_automatic_face_capture(self):
        """Démarre le processus d'enregistrement automatique des visages."""
        if not self.is_capturing:
            QMessageBox.warning(self, "Avertissement", "Veuillez d'abord ouvrir la caméra.")
            return

        self.photos_captured_current_session = 0
        self.is_recording_faces = True
        self._toggle_buttons(start=False, stop=True, start_record=False, stop_record=True)
        QMessageBox.information(self, "Enregistrement Automatique",
                                f"L'enregistrement automatique de {self.photo_count_to_capture} visages a commencé.")

    def _stop_automatic_face_capture(self):
        """Arrête le processus d'enregistrement automatique des visages."""
        if self.is_recording_faces:
            self.is_recording_faces = False
            self._toggle_buttons(start=False, stop=True, start_record=True, stop_record=False)
            QMessageBox.information(self, "Enregistrement Arrêté",
                                    "L'enregistrement automatique des visages a été arrêté.")
            self.photos_captured_current_session = 0

    def _change_output_directory(self):
        """Permet à l'utilisateur de choisir un nouveau répertoire de sauvegarde pour les images."""
        new_directory = QFileDialog.getExistingDirectory(self, "Choisir le répertoire", self.output_directory)
        if new_directory:
            self.output_directory = new_directory
            QMessageBox.information(self, "Info", f"Répertoire changé pour : {self.output_directory}")

    def _toggle_fullscreen(self):
        """Active ou désactive le mode plein écran."""
        if not self.is_fullscreen:
            self.showFullScreen()
            self.fullscreen_button.setText("Quitter Plein Écran")
        else:
            self.showNormal()
            self.fullscreen_button.setText("Plein Écran")
        self.is_fullscreen = not self.is_fullscreen

    def _toggle_buttons(self, start=False, stop=False, start_record=False, stop_record=False):
        """Contrôle l'état activé/désactivé des boutons de l'interface."""
        self.start_button.setEnabled(start)
        self.stop_button.setEnabled(stop)
        self.start_recording_button.setEnabled(start_record)
        self.stop_recording_button.setEnabled(stop_record)

    def load_stylesheet(self, path: str) -> None:
        """Charge une feuille de style CSS pour l'interface."""
        try:
            with open(path, "r") as file:
                self.setStyleSheet(file.read())
        except FileNotFoundError:
            QMessageBox.warning(self, "Erreur", f"Feuille de style non trouvée : {path}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur Critique", f"Impossible de charger la feuille de style : {e}")