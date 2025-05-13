from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
import cv2
import os
import numpy as np

class ACCER_WEBCAMERA(QMainWindow):
    login_page_signal = Signal()
    mainwindow_signal = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("ACCEDER A LA CAMERA ET RECONNAISSANCE FACIALE")
        self.screen = QApplication.primaryScreen().availableGeometry()
        self.is_maximized = False
        self.webcam = None
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_frame)
        self.face_cascade = cv2.CascadeClassifier("Views/image/haarcascade_frontalface_default.xml")
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.training_file = None
        self.is_recognizing = False
        self.camera_active = False
        self.recognition_threshold = 50  # Augmenter le seuil par défaut
        self.training_image_size = (100, 100) # Taille des images d'entraînement (à ajuster)
        self._setup_ui()
        self.load_stylesheet("Styles/webcam_style.css")
        self._handle_resize(None)

    def _create_button(self, text, callback, enabled=True):
        button = QPushButton(text)
        button.clicked.connect(callback)
        button.setEnabled(enabled)
        return button

    def _create_checkbox(self, text, enabled=False, checked=False):
        checkbox = QCheckBox(text)
        checkbox.setEnabled(enabled)
        checkbox.setChecked(checked)
        return checkbox

    def _create_label(self, alignment=Qt.AlignmentFlag.AlignCenter, scaled_contents=True):
        label = QLabel(self)
        label.setAlignment(alignment)
        label.setScaledContents(scaled_contents)
        return label

    def _setup_ui(self):
        self.central_widget = QWidget()
        main_layout = QHBoxLayout(self.central_widget)

        self.webcam_label = self._create_label()
        main_layout.addWidget(self.webcam_label, 1)

        controls_frame = QFrame()
        controls_layout = QVBoxLayout(controls_frame)
        controls_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.url_input = QLineEdit("Ajouter l'URL de la camera...")
        self.activate_url_button = self._create_button("Activer URL", self._start_camera_from_url)
        self.open_camera_button = self._create_button("Ouvrir Webcam (Par Défaut)", self._start_default_camera)
        self.close_camera_button = self._create_button("Fermer Webcam", self._stop_camera)
        self.fullscreen_button = self._create_button("Plein Écran", self._toggle_camera_size)
        self.file_button = self._create_button("Sélectionner Fichier YAML", self._select_training_file)
        self.recognize_button = self._create_button("Démarrer Reconnaissance", self._toggle_reconnaissance, enabled=False)
        self.mainwindow_button = self._create_button("MainWindow", self._back_to_login_main_window)
        self.camera_status_checkbox = self._create_checkbox("Caméra Active")

        for widget in [self.url_input, self.activate_url_button, self.open_camera_button,
                       self.close_camera_button, self.fullscreen_button, self.file_button,
                       self.recognize_button, self.mainwindow_button, self.camera_status_checkbox]:
            controls_layout.addWidget(widget)
        controls_layout.addStretch(1)
        main_layout.addWidget(controls_frame)

        self._setup_menu_bar()
        self.resizeEvent = self._handle_resize
        self.setCentralWidget(self.central_widget)

    def _setup_menu_bar(self):
        self.menu_bar = QMenuBar(self)
        self.options_menu = QMenu("Options", self.menu_bar)
        self.menu_bar.addMenu(self.options_menu)
        self.setMenuBar(self.menu_bar)
        self.menu_bar.hide()

    def _handle_resize(self, event):
        controls_frame = self.findChild(QFrame)
        if self.width() < 600:
            controls_frame.hide()
            self.menu_bar.show()
            self.options_menu.clear()
            for button in [self.activate_url_button, self.open_camera_button,
                           self.close_camera_button, self.fullscreen_button,
                           self.file_button, self.recognize_button,
                           self.mainwindow_button]:
                action = QAction(button.text(), self)
                action.triggered.connect(button.clicked)
                self.options_menu.addAction(action)
        else:
            controls_frame.show()
            self.menu_bar.hide()

    def load_stylesheet(self, path: str) -> None:
        try:
            with open(path, "r") as file:
                self.setStyleSheet(file.read())
        except FileNotFoundError:
            QMessageBox.warning(self, "Erreur", f"Feuille de style non trouvée : {path}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur Critique", f"Impossible de charger la feuille de style : {e}")

    def _start_default_camera(self):
        self._start_camera(0)

    def _start_camera_from_url(self):
        url = self.url_input.text().strip()
        if not url or url == "Ajouter l'URL de la camera...":
            QMessageBox.warning(self, "Avertissement", "Veuillez entrer l'URL de la caméra.")
            return
        self._start_camera(url)

    def _start_camera(self, camera_source):
        self._stop_camera()
        self.webcam = cv2.VideoCapture(camera_source)
        if not self.webcam.isOpened():
            QMessageBox.critical(self, "Erreur", f"Impossible d'ouvrir la caméra à l'adresse : {camera_source}")
            self._reset_camera_ui()
            return
        QMessageBox.information(self, "Info", f"Caméra connectée à : {camera_source}")
        self.url_input.clear()
        self.timer.start(30)
        self._update_camera_status(True)

    def _stop_camera(self):
        if self.webcam and self.webcam.isOpened():
            self.timer.stop()
            self.webcam.release()
            self._reset_camera_ui("Webcam fermée.")
        elif self.camera_active:
            self._reset_camera_ui("Aucune webcam n'est active.")

    def _reset_camera_ui(self, message=""):
        self.webcam = None
        self.webcam_label.clear()
        self._update_camera_status(False)
        if message:
            QMessageBox.information(self, "Info", message)

    def _update_camera_status(self, is_active):
        self.camera_active = is_active
        self.camera_status_checkbox.setChecked(is_active)

    def _update_frame(self):
        if self.webcam and self.webcam.isOpened():
            success, frame = self.webcam.read()
            if success:
                self._update_camera_status(True)
                if self.is_recognizing and self.face_cascade and self.recognizer and self.training_file:
                    frame = self._recognize_faces(frame)
                self._display_frame(frame)
            else:
                self._handle_camera_error("Flux vidéo interrompu.")
        else:
            self._update_camera_status(False)

    def _handle_camera_error(self, message):
        self._stop_camera()
        QMessageBox.warning(self, "Avertissement", message)
        self._update_camera_status(False)

    def _recognize_faces(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(30, 30))
        for x, y, w, h in faces:
            face_roi = gray[y:y + h, x:x + w]
            if face_roi.size > 0:
                try:
                    # Redimensionner la ROI à la taille des images d'entraînement
                    resized_face = cv2.resize(face_roi, self.training_image_size)

                    chauffeur_id, confidence = self.recognizer.predict(resized_face)
                    confidence_percent = 100 - int(confidence)
                    color = (0, 255, 0) if confidence_percent > self.recognition_threshold else (0, 0, 255)
                    label = f"ID: {chauffeur_id} ({confidence_percent:.2f}%)" if confidence_percent > self.recognition_threshold else "Inconnu"
                    cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                    cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_COMPLEX, 0.7, color, 2)
                except Exception as e:
                    print(f"Erreur lors de la prédiction: {e}")
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                    cv2.putText(frame, "Erreur Prediction", (x, y - 10), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 255), 2)
        return frame

    def _display_frame(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        q_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        scaled_image = q_image.scaled(self.webcam_label.width(), self.webcam_label.height(),
                                       Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.webcam_label.setPixmap(QPixmap.fromImage(scaled_image))

    def _toggle_camera_size(self):
        self.is_maximized = not self.is_maximized
        if self.is_maximized:
            self.showFullScreen()
        else:
            self.showNormal()

    def _back_to_login_page(self):
        self.login_page_signal.emit()

    def _back_to_login_main_window(self):
        self.mainwindow_signal.emit()

    def _select_training_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Sélectionner le fichier YAML d'entraînement", "", "Fichiers YAML (*.yml *.yaml)")
        if file_path:
            self.training_file = file_path
            try:
                self.recognizer.read(self.training_file)
                self.recognize_button.setEnabled(True)
                QMessageBox.information(self, "Succès", f"Fichier chargé: {os.path.basename(self.training_file)}")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement du fichier: {e}")
                self.training_file = None
                self.recognize_button.setEnabled(False)

    def _toggle_reconnaissance(self):
        if not self.webcam or not self.webcam.isOpened():
            QMessageBox.warning(self, "Avertissement", "Veuillez d'abord démarrer la webcam.")
            return
        if not self.training_file:
            QMessageBox.warning(self, "Avertissement", "Veuillez sélectionner un fichier YAML d'entraînement.")
            return
        self.is_recognizing = not self.is_recognizing
        self.recognize_button.setText("Arrêter Reconnaissance" if self.is_recognizing else "Démarrer Reconnaissance")
        self.file_button.setEnabled(not self.is_recognizing)

