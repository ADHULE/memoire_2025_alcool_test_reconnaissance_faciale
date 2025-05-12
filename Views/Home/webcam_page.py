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
        self.timer.timeout.connect(self.update_frame)

        self.face_cascade = cv2.CascadeClassifier(
            "Views/image/haarcascade_frontalface_default.xml")
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.training_file = None
        self.is_recognizing = False
        self.camera_active = False

        self.buttons = []

        self.setup_ui()

    def setup_ui(self):
        self.central_widget = QWidget()
        main_layout = QHBoxLayout(self.central_widget)

        # Label pour la webcam
        self.webcam_label = QLabel(self)
        self.webcam_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.webcam_label.setScaledContents(True)
        # self.webcam_label.setStyleSheet("background-color: black;")
        main_layout.addWidget(self.webcam_label, 1)

        # Cadre pour les contrôles à droite
        controls_frame = QFrame()
        controls_layout = QVBoxLayout(controls_frame)
        controls_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.url_input = QLineEdit("Ajouter l'URL de la camera...")
        self.activate_url_button = QPushButton("Activer URL")
        self.open_camera_button = QPushButton("Ouvrir Webcam (Par Défaut)")
        self.close_camera_button = QPushButton("Fermer Webcam")
        self.fullscreen_button = QPushButton("Plein Écran")
        self.file_button = QPushButton("Sélectionner Fichier YAML")
        self.recognize_button = QPushButton("Démarrer Reconnaissance")
        self.recognize_button.setEnabled(False)
        self.mainwindow_button = QPushButton("MainWindow")

        # Checkbox pour l'état de la caméra
        self.camera_status_checkbox = QCheckBox("Caméra Active")
        self.camera_status_checkbox.setEnabled(False)

        self.activate_url_button.clicked.connect(self.start_camera)
        self.open_camera_button.clicked.connect(self.start_default_camera)
        self.close_camera_button.clicked.connect(self.stop_camera)
        self.fullscreen_button.clicked.connect(self.toggle_camera_size)
        self.file_button.clicked.connect(self.select_training_file)
        self.recognize_button.clicked.connect(self.toggle_reconnaissance)
        self.mainwindow_button.clicked.connect(self.back_to_login_main_window)

        controls_layout.addWidget(self.url_input)
        controls_layout.addWidget(self.activate_url_button)
        controls_layout.addWidget(self.open_camera_button)
        controls_layout.addWidget(self.close_camera_button)
        controls_layout.addWidget(self.fullscreen_button)
        controls_layout.addWidget(self.file_button)
        controls_layout.addWidget(self.recognize_button)
        controls_layout.addWidget(self.mainwindow_button)
        controls_layout.addWidget(self.camera_status_checkbox)
        controls_layout.addStretch(1)

        main_layout.addWidget(controls_frame)

        # Menu adaptatif
        self.menu_bar = QMenuBar(self)
        self.options_menu = QMenu("Options", self.menu_bar)
        self.menu_bar.addMenu(self.options_menu)
        self.setMenuBar(self.menu_bar)
        self.menu_bar.hide()

        self.resizeEvent = self.handle_resize

        self.setCentralWidget(self.central_widget)
        self.load_stylesheet("Styles/webcam_style.css")
        self.handle_resize(None)

    def handle_resize(self, event):
        if self.width() < 600:
            self.findChild(QFrame).hide()
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
            self.findChild(QFrame).show()
            self.menu_bar.hide()

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

    def start_default_camera(self):
        self._start_camera(0)  # Utilisez 0 pour la caméra par défaut

    def start_camera(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(
                self, "Avertissement", "Veuillez entrer l'URL de la caméra."
            )
            return
        self._start_camera(url)

    def _start_camera(self, camera_source):
        if self.webcam and self.webcam.isOpened():
            self.stop_camera()  # Fermer la caméra actuelle si elle est ouverte

        self.webcam = cv2.VideoCapture(camera_source)

        if not self.webcam.isOpened():
            QMessageBox.critical(
                self, "Erreur", f"Impossible d'ouvrir la caméra à l'adresse : {camera_source}"
            )
            self.webcam = None
            self.webcam_label.clear()
            self.camera_active = False
            self.camera_status_checkbox.setChecked(False)
            return

        QMessageBox.information(
            self, "Info", f"Caméra connectée à : {camera_source}"
        )
        self.url_input.clear()  # Vider le champ de saisie après la connexion
        self.timer.start(30)
        self.camera_active = True
        self.camera_status_checkbox.setChecked(True)

    def stop_camera(self):
        if self.webcam and self.webcam.isOpened():
            self.timer.stop()
            self.webcam.release()
            self.webcam = None
            self.webcam_label.clear()
            self.camera_active = False
            self.camera_status_checkbox.setChecked(False)
            QMessageBox.information(self, "Info", "Webcam fermée.")
        else:
            QMessageBox.warning(self, "Avertissement", "Aucune webcam n'est active.")
            self.camera_active = False
            self.camera_status_checkbox.setChecked(False)

    def update_frame(self):
        if self.webcam and self.webcam.isOpened():
            success, frame = self.webcam.read()
            if success:
                self.camera_active = True
                self.camera_status_checkbox.setChecked(True)
                if self.is_recognizing and self.face_cascade and self.recognizer and self.training_file:
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    faces = self.face_cascade.detectMultiScale(
                        gray, scaleFactor=1.3, minNeighbors=5, minSize=(30, 30))

                    for (x, y, w, h) in faces:
                        face_roi = gray[y:y + h, x:x + w]
                        if face_roi.size == 0:
                            continue

                        try:
                            chauffeur_id, confidence = self.recognizer.predict(
                                face_roi)
                            confidence_percent = 100 - int(confidence)
                            threshold = 60

                            if confidence_percent > threshold:
                                cv2.rectangle(
                                    frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                                cv2.putText(frame, f"ID: {chauffeur_id} ({confidence_percent}%)", (
                                    x, y - 10), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 127), 2)
                            else:
                                cv2.rectangle(
                                    frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                                cv2.putText(
                                    frame, "Inconnu", (x, y - 10), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 255), 2)

                        except Exception as e:
                            print(f"Erreur lors de la prédiction: {e}")
                            cv2.rectangle(
                                frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                            cv2.putText(frame, "Erreur Prediction", (x, y - 10),
                                        cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 255), 2)

                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = frame.shape
                bytes_per_line = ch * w
                q_image = QImage(
                    frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888
                )
                scaled_image = q_image.scaled(
                    self.webcam_label.width(),
                    self.webcam_label.height(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                self.webcam_label.setPixmap(QPixmap.fromImage(scaled_image))
            else:
                self.stop_camera()
                QMessageBox.warning(
                    self, "Avertissement", "Flux vidéo interrompu."
                )
                self.camera_active = False
                self.camera_status_checkbox.setChecked(False)
        else:
            self.camera_active = False
            self.camera_status_checkbox.setChecked(False)

    def toggle_camera_size(self):
        if not self.is_maximized:
            self.showFullScreen()
            self.is_maximized = True
        else:
            self.showNormal()
            self.is_maximized = False

    def back_to_login_page(self):
        self.login_page_signal.emit()

    def back_to_login_main_window(self):
        self.mainwindow_signal.emit()

    def select_training_file(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self, "Sélectionner le fichier YAML d'entraînement", "", "Fichiers YAML (*.yml *.yaml)"
        )
        if file_path:
            self.training_file = file_path
            try:
                self.recognizer.read(self.training_file)
                self.recognize_button.setEnabled(True)
                QMessageBox.information(
                    self, "Succès", f"Fichier chargé: {os.path.basename(self.training_file)}")
            except Exception as e:
                QMessageBox.critical(
                    self, "Erreur", f"Erreur lors du chargement du fichier: {e}")
                self.training_file = None
                self.recognize_button.setEnabled(False)

    def toggle_reconnaissance(self):
        if not self.webcam or not self.webcam.isOpened():
            QMessageBox.warning(self, "Avertissement",
                                "Veuillez d'abord démarrer la webcam.")
            return

        if not self.training_file:
            QMessageBox.warning(
                self, "Avertissement", "Veuillez sélectionner un fichier YAML d'entraînement.")
            return

        self.is_recognizing = not self.is_recognizing
        if self.is_recognizing:
            self.recognize_button.setText("Arrêter Reconnaissance")
            self.file_button.setEnabled(False)
        else:
            self.recognize_button.setText("Démarrer Reconnaissance")
            self.file_button.setEnabled(True)
