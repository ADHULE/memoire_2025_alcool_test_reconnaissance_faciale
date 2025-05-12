from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QMessageBox, QFileDialog
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt, QTimer, Signal
import cv2
import os
import datetime

class CameraView(QWidget):
    """Interface pour la capture d'images de visage."""

    image_captured_signal = Signal(str)
    finished = Signal(str)  # Ajout du signal 'finished'

    def __init__(self, parent=None, identifier=None):
        super().__init__(parent)
        self.setWindowTitle("Enregistrement du Visage")
        self.identifier = identifier
        self.capture, self.current_frame = None, None
        self.is_capturing, self.is_fullscreen = False, False
        self.output_directory = "captured_faces"
        self.target_size = (100, 100)  # Taille cible pour les images de visage enregistrées
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)

        main_layout = QHBoxLayout(self)
        self.video_label = self._create_label(alignment=Qt.AlignCenter)
        main_layout.addWidget(self.video_label, 1)

        self.controls_widget = QWidget()
        self.controls_layout = QVBoxLayout(self.controls_widget)
        main_layout.addWidget(self.controls_widget, 0)

        self.start_button = self._create_button("Ouvrir Caméra", self._start_camera)
        self.stop_button = self._create_button("Fermer Caméra", self._stop_camera, enabled=False)
        self.capture_button = self._create_button("Enregistrer Visage", self._capture_and_save_face, enabled=False)
        self.fullscreen_button = self._create_button("Plein Écran", self._toggle_fullscreen)
        self.change_dir_button = self._create_button("Changer Répertoire", self._change_output_directory)

        self.controls_layout.addWidget(self.start_button)
        self.controls_layout.addWidget(self.stop_button)
        self.controls_layout.addWidget(self.capture_button)
        self.controls_layout.addWidget(self.fullscreen_button)
        self.controls_layout.addWidget(self.change_dir_button)
        self.controls_layout.addStretch(1)

        self.setLayout(main_layout)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_frame)
        self.load_stylesheet("Styles/webcam_style.css")

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

    def _start_camera(self):
        """Démarre la capture vidéo."""
        self.capture = cv2.VideoCapture(0)
        if not self.capture.isOpened():
            QMessageBox.critical(self, "Erreur", "Impossible d'ouvrir la caméra.")
            return
        self.is_capturing = True
        self.timer.start(30)
        self._toggle_buttons(start=False, stop=True, capture=True)

    def _stop_camera(self):
        """Arrête la capture vidéo."""
        if self.is_capturing and self.capture.isOpened():
            self.timer.stop()
            self.capture.release()
            self.capture = None
            self.is_capturing = False
            self.video_label.clear()
            self._toggle_buttons(start=True, stop=False, capture=False)

    def _update_frame(self):
        """Met à jour l'affichage vidéo en direct en détectant les visages."""
        if self.is_capturing and self.capture.isOpened():
            ret, frame = self.capture.read()
            if ret:
                self.current_frame = frame  # Ajout pour permettre la capture correcte
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

    def _capture_and_save_face(self):
        """Capture un visage, le redimensionne et l'enregistre en noir et blanc."""
        if self.is_capturing and self.current_frame is not None:
            gray_frame = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray_frame, scaleFactor=1.3, minNeighbors=5, minSize=(30, 30))

            if len(faces) > 0:
                (x, y, w, h) = faces[0]
                face_roi_gray = gray_frame[y:y + h, x:x + w]  # Capture en niveaux de gris
                resized_face_gray = cv2.resize(face_roi_gray, self.target_size)
                filename = f"{self.identifier}_face_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png" if self.identifier else f"face_capture_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                filepath = os.path.join(self.output_directory, filename)
                cv2.imwrite(filepath, resized_face_gray)  # Enregistrement en noir et blanc
                QMessageBox.information(self, "Succès", f"Visage enregistré sous : {filepath} (Taille: {self.target_size[0]}x{self.target_size[1]})")
                self.image_captured_signal.emit(filepath)
                self.finished.emit(filepath)  # Émission du signal 'finished'
            else:
                QMessageBox.warning(self, "Avertissement", "Aucun visage détecté.")

    def _change_output_directory(self):
        """Change le répertoire de sauvegarde des images."""
        new_directory = QFileDialog.getExistingDirectory(self, "Choisir le répertoire", self.output_directory)
        if new_directory:
            self.output_directory = new_directory
            QMessageBox.information(self, "Info", f"Répertoire changé pour : {self.output_directory}")

    def _toggle_fullscreen(self):
        """Active/désactive le mode plein écran."""
        self.showFullScreen() if not self.is_fullscreen else self.showNormal()
        self.fullscreen_button.setText("Quitter Plein Écran" if not self.is_fullscreen else "Plein Écran")
        self.is_fullscreen = not self.is_fullscreen

    def _toggle_buttons(self, start=False, stop=False, capture=False):
        """Active/désactive les boutons selon l'état de la capture."""
        self.start_button.setEnabled(start)
        self.stop_button.setEnabled(stop)
        self.capture_button.setEnabled(capture)

    def load_stylesheet(self, path: str) -> None:
        try:
            with open(path, "r") as file:
                self.setStyleSheet(file.read())
        except FileNotFoundError:
            QMessageBox.warning(
                self, "Erreur", f"Feuille de style non trouvée : {path}"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Erreur Critique",
                f"Impossible de charger la feuille de style : {e}",
            )
