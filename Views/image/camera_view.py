from PySide6.QtWidgets import *
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
        self.target_size = (300, 400)  # Taille cible pour les images de visage enregistrées
        self.face_cascade = cv2.CascadeClassifier("Views/image/haarcascade_frontalface_default.xml")
        self.camera_active = False # Pour suivre l'état de la caméra

        # --- Nouvelle fonctionnalité : Compteur de photos pour l'enregistrement automatique ---
        self.photo_count_to_capture = 1  # Nombre de photos à capturer spécifié par l'utilisateur
        self.photos_captured_current_session = 0 # Compteur des photos déjà capturées dans la session
        self.is_recording_faces = False # Indicateur si l'enregistrement automatique est en cours
        # --- Fin de la nouvelle fonctionnalité ---

        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)

        main_layout = QHBoxLayout(self)

        # Zone d'affichage vidéo
        self.video_label = self._create_label(alignment=Qt.AlignCenter)
        main_layout.addWidget(self.video_label, 1)

        # Zone de contrôles
        self.controls_widget = QWidget()
        self.controls_layout = QVBoxLayout(self.controls_widget)

        # Sous-layout pour l'ajout d'URL
        self.url_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_layout.addStretch()
        self.url_input.setPlaceholderText("Entrer l'URL de la caméra IP")
        self.add_url_button = self._create_button("Ajouter URL", self.start_camera)
        self.url_layout.addWidget(self.url_input)
        self.url_layout.addWidget(self.add_url_button)
        self.controls_layout.addLayout(self.url_layout)

        # Bouton pour la caméra par défaut
        self.default_camera_button = self._create_button("Caméra par Défaut", self.start_default_camera)
        self.controls_layout.addWidget(self.default_camera_button)

        # Séparateur visuel
        
        self.start_button = self._create_button("Ouvrir Caméra (Indice 0)", self._start_camera, enabled=True)
        self.stop_button = self._create_button("Fermer Caméra", self._stop_camera, enabled=False)
        # Bouton pour démarrer l'enregistrement automatique des visages
        self.start_recording_button = self._create_button("Démarrer Enregistrement Auto", self._start_automatic_face_capture, enabled=False)
        # Nouveau bouton pour arrêter l'enregistrement automatique
        self.stop_recording_button = self._create_button("Arrêter Enregistrement Auto", self._stop_automatic_face_capture, enabled=False)
        self.fullscreen_button = self._create_button("Plein Écran", self._toggle_fullscreen)
        self.change_dir_button = self._create_button("Changer Répertoire", self._change_output_directory)

        # --- Nouvelle fonctionnalité : Champs pour le nombre de photos ---
        self.photo_count_layout = QHBoxLayout()
        self.photo_count_label = QLabel("Nombre de photos à capturer:")
        self.photo_count_input = QSpinBox()
        self.photo_count_input.setMinimum(1)
        self.photo_count_input.setMaximum(100)
        self.photo_count_input.setValue(1)
        self.photo_count_input.valueChanged.connect(self._update_photo_count)
        self.photo_count_layout.addWidget(self.photo_count_label)
        self.photo_count_layout.addWidget(self.photo_count_input)
        self.controls_layout.addLayout(self.photo_count_layout)
        # --- Fin de la nouvelle fonctionnalité ---

        self.controls_layout.addWidget(self.start_button)
        self.controls_layout.addWidget(self.stop_button)
        self.controls_layout.addWidget(self.start_recording_button) # Ajout du nouveau bouton
        self.controls_layout.addWidget(self.stop_recording_button) # Ajout du nouveau bouton
        self.controls_layout.addWidget(self.fullscreen_button)
        self.controls_layout.addWidget(self.change_dir_button)
        self.controls_layout.addStretch(1)

        main_layout.addWidget(self.controls_widget, 0)

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
        """Démarre la capture vidéo depuis la caméra par défaut (indice 0)."""
        self._open_camera(0)

    def start_default_camera(self):
        """Tente de démarrer la caméra par défaut (indice 0)."""
        self._open_camera(0)

    def start_camera(self):
        """Tente de démarrer la caméra à partir de l'URL fournie."""
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(
                self, "Avertissement", "Veuillez entrer l'URL de la caméra."
            )
            return
        self._open_camera(url)

    def _open_camera(self, camera_source):
        """Ouvre la caméra spécifiée par la source (indice ou URL)."""
        if self.capture and self.capture.isOpened():
            self._stop_camera()  # Fermer la caméra actuelle si elle est ouverte

        self.capture = cv2.VideoCapture(camera_source)

        if not self.capture.isOpened():
            QMessageBox.critical(
                self, "Erreur", f"Impossible d'ouvrir la caméra à l'adresse : {camera_source}"
            )
            self.capture = None
            self.video_label.clear()
            self.is_capturing = False
            self._toggle_buttons(start=True, stop=False, start_record=False, stop_record=False)
            return

        QMessageBox.information(
            self, "Info", f"Caméra connectée à : {camera_source}"
        )
        if isinstance(camera_source, str):
            self.url_input.clear()  # Vider le champ de saisie après la connexion
        self.is_capturing = True
        self.timer.start(30)
        self._toggle_buttons(start=False, stop=True, start_record=True, stop_record=False)
        # Réinitialiser le compteur après l'ouverture de la caméra
        self.photos_captured_current_session = 0
        self.is_recording_faces = False # S'assurer que l'enregistrement automatique est désactivé

    def _stop_camera(self):
        """Arrête la capture vidéo."""
        if self.is_capturing and self.capture and self.capture.isOpened():
            self.timer.stop()
            self.capture.release()
            self.capture = None
            self.is_capturing = False
            self.video_label.clear()
            self._toggle_buttons(start=True, stop=False, start_record=False, stop_record=False)
            # Réinitialiser le compteur et l'état d'enregistrement après l'arrêt de la caméra
            self.photos_captured_current_session = 0
            self.is_recording_faces = False

    def _update_frame(self):
        """Met à jour l'affichage vidéo en direct en détectant les visages."""
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

                # --- Nouvelle fonctionnalité : Enregistrement automatique dans la boucle de mise à jour ---
                if self.is_recording_faces and self.photos_captured_current_session < self.photo_count_to_capture:
                    # Tenter de capturer une photo si un visage est détecté
                    if len(faces) > 0:
                        (x, y, w, h) = faces[0]
                        face_roi_gray = gray[y:y + h, x:x + w]
                        resized_face_gray = cv2.resize(face_roi_gray, self.target_size)
                        
                        filename = f"{self.identifier}_face_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{self.photos_captured_current_session + 1}.png" \
                                    if self.identifier else f"face_capture_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{self.photos_captured_current_session + 1}.png"
                        
                        filepath = os.path.join(self.output_directory, filename)
                        cv2.imwrite(filepath, resized_face_gray)
                        
                        self.photos_captured_current_session += 1
                        QMessageBox.information(self, "Capture Automatique", f"Visage {self.photos_captured_current_session}/{self.photo_count_to_capture} enregistré sous : {filepath}")
                        self.image_captured_signal.emit(filepath)
                        
                        if self.photos_captured_current_session >= self.photo_count_to_capture:
                            self._stop_automatic_face_capture() # Arrêter l'enregistrement une fois toutes les photos capturées
                            QMessageBox.information(self, "Enregistrement Terminé", f"Toutes les {self.photo_count_to_capture} photos ont été capturées automatiquement.")
                            self.finished.emit("Automatic multiple captures completed.")
                # --- Fin de la nouvelle fonctionnalité ---

            else:
                self._stop_camera()
                QMessageBox.warning(self, "Avertissement", "Flux vidéo terminé ou interrompu.")

    def _update_photo_count(self, value):
        """Met à jour le nombre de photos à capturer en fonction de la valeur de QSpinBox."""
        self.photo_count_to_capture = value

    # --- Nouvelle fonctionnalité : Démarrer et arrêter l'enregistrement automatique ---
    def _start_automatic_face_capture(self):
        """Démarre l'enregistrement automatique des visages."""
        if not self.is_capturing:
            QMessageBox.warning(self, "Avertissement", "Veuillez d'abord ouvrir la caméra.")
            return

        self.photos_captured_current_session = 0 # Réinitialiser le compteur au début de l'enregistrement
        self.is_recording_faces = True
        self._toggle_buttons(start=False, stop=True, start_record=False, stop_record=True)
        QMessageBox.information(self, "Enregistrement Automatique", f"L'enregistrement automatique de {self.photo_count_to_capture} visages a commencé.")

    def _stop_automatic_face_capture(self):
        """Arrête l'enregistrement automatique des visages."""
        if self.is_recording_faces:
            self.is_recording_faces = False
            self._toggle_buttons(start=False, stop=True, start_record=True, stop_record=False)
            QMessageBox.information(self, "Enregistrement Arrêté", "L'enregistrement automatique des visages a été arrêté.")
            self.photos_captured_current_session = 0 # Réinitialiser le compteur
    # --- Fin de la nouvelle fonctionnalité ---

    def _capture_and_save_face(self):
        # Cette fonction est l'ancienne logique de capture unique et n'est plus directement appelée.
        # Elle est conservée ici pour référence mais la nouvelle logique utilise _start_automatic_face_capture
        # et la boucle dans _update_frame.
        pass # La logique est maintenant dans _update_frame

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

    # Mise à jour de la fonction pour contrôler les nouveaux boutons
    def _toggle_buttons(self, start=False, stop=False, start_record=False, stop_record=False):
        """Active/désactive les boutons selon l'état de la capture et de l'enregistrement."""
        self.start_button.setEnabled(start)
        self.stop_button.setEnabled(stop)
        self.start_recording_button.setEnabled(start_record) # Contrôle du bouton Démarrer Enregistrement Auto
        self.stop_recording_button.setEnabled(stop_record) # Contrôle du bouton Arrêter Enregistrement Auto

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