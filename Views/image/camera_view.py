from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QMessageBox, QFileDialog
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt, QTimer, Signal
import cv2
import os
import datetime

class CameraView(QWidget):
    """Interface pour la capture d'images via la caméra."""

    image_captured_signal = Signal(str)
    finished = Signal(str) # Ajout du signal 'finished'

    def __init__(self, parent=None, identifier=None):
        super().__init__(parent)
        self.setWindowTitle("Enregistrement d'Images")
        self.identifier = identifier
        self.capture, self.current_frame = None, None
        self.is_capturing, self.is_fullscreen = False, False
        self.output_directory = "captured_images"

        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)

        main_layout = QHBoxLayout(self)
        self.video_label = self._create_label(alignment=Qt.AlignCenter)
        main_layout.addWidget(self.video_label, 1)

        self.controls_widget = QWidget()
        self.controls_layout = QVBoxLayout(self.controls_widget)
        main_layout.addWidget(self.controls_widget, 0)

        self.start_button = self._create_button("Ouvrir Caméra", self.start_camera)
        self.stop_button = self._create_button("Fermer Caméra", self.stop_camera, enabled=False)
        self.capture_button = self._create_button("Enregistrer Image", self.capture_and_save_image, enabled=False)
        self.fullscreen_button = self._create_button("Plein Écran", self.toggle_fullscreen)
        self.change_dir_button = self._create_button("Changer Répertoire", self.change_output_directory)

        self.controls_layout.addWidget(self.start_button)
        self.controls_layout.addWidget(self.stop_button)
        self.controls_layout.addWidget(self.capture_button)
        self.controls_layout.addWidget(self.fullscreen_button)
        self.controls_layout.addWidget(self.change_dir_button)
        self.controls_layout.addStretch(1)

        self.setLayout(main_layout)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)

    def set_chauffeur_id(self, chauffeur_id):
        """Définit l'identifiant du chauffeur associé à la capture."""
        self.identifier = chauffeur_id

    def _create_label(self, alignment=None):
        label = QLabel()
        if alignment:
            label.setAlignment(alignment)
        return label

    def _create_button(self, text, callback, enabled=True):
        button = QPushButton(text)
        button.clicked.connect(callback)
        button.setEnabled(enabled)
        return button

    def start_camera(self):
        """Démarre la capture vidéo."""
        self.capture = cv2.VideoCapture(0)
        if not self.capture.isOpened():
            QMessageBox.critical(self, "Erreur", "Impossible d'ouvrir la caméra.")
            return
        self.is_capturing = True
        self.timer.start(30)
        self._toggle_buttons(start=False, stop=True, capture=True)

    def stop_camera(self):
        """Arrête la capture vidéo."""
        if self.is_capturing and self.capture.isOpened():
            self.timer.stop()
            self.capture.release()
            self.capture = None
            self.is_capturing = False
            self.video_label.clear()
            self._toggle_buttons(start=True, stop=False, capture=False)

    def update_frame(self):
        """Met à jour l'affichage vidéo en direct."""
        if self.is_capturing and self.capture.isOpened():
            ret, frame = self.capture.read()
            if ret:
                self.current_frame = frame
                q_image = QImage(frame.data, frame.shape[1], frame.shape[0], frame.shape[1] * 3, QImage.Format_BGR888)
                self.video_label.setPixmap(QPixmap.fromImage(q_image).scaled(self.video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def capture_and_save_image(self):
        """Capture et enregistre l'image actuelle."""
        if self.current_frame is not None:
            filename = f"{self.identifier}_capture_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png" if self.identifier else f"capture_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = os.path.join(self.output_directory, filename)
            cv2.imwrite(filepath, self.current_frame)
            QMessageBox.information(self, "Succès", f"Image enregistrée sous : {filepath}")
            self.image_captured_signal.emit(filepath)
            self.finished.emit(filepath) # Émission du signal 'finished'

    def change_output_directory(self):
        """Change le répertoire de sauvegarde des images."""
        new_directory = QFileDialog.getExistingDirectory(self, "Choisir le répertoire", self.output_directory)
        if new_directory:
            self.output_directory = new_directory
            QMessageBox.information(self, "Info", f"Répertoire changé pour : {self.output_directory}")

    def toggle_fullscreen(self):
        """Active/désactive le mode plein écran."""
        self.showFullScreen() if not self.is_fullscreen else self.showNormal()
        self.fullscreen_button.setText("Quitter Plein Écran" if not self.is_fullscreen else "Plein Écran")
        self.is_fullscreen = not self.is_fullscreen

    def _toggle_buttons(self, start=False, stop=False, capture=False):
        """Active/désactive les boutons selon l'état de la capture."""
        self.start_button.setEnabled(start)
        self.stop_button.setEnabled(stop)
        self.capture_button.setEnabled(capture)