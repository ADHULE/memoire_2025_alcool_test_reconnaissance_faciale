from PySide6.QtWidgets import*
 
from PySide6.QtGui import *
from PySide6.QtCore import *

import cv2
import os
import numpy as np

# Charger les informations pour la reconnaissance faciale (si nécessaire, sinon commenter)
# from Controllers.chauffeur_controller import CHAUFFEUR_CONTROLLER
# from Controllers.image_controller import IMAGE_CONTROLLER


class ACCER_WEBCAMERA(QMainWindow):
    # Déclaration correcte du signal pour la connexion à une autre interface
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

        self.face_cascade = cv2.CascadeClassifier( "Views/image/haarcascade_frontalface_default.xml")
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.training_file = None
        self.is_recognizing = False

        self.buttons = []

        self.setup_ui()

    def setup_ui(self):
        self.central_widget = QWidget()
        main_layout = QHBoxLayout(self.central_widget)

        # Label pour la webcam
        self.webcam_label = QLabel(self)
        self.webcam_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.webcam_label.setScaledContents(True)
        self.webcam_label.setStyleSheet("background-color: black;")
        main_layout.addWidget(self.webcam_label, 1)

        # Cadre pour les boutons à droite
        self.buttons_frame = QFrame()
        self.buttons_layout = QVBoxLayout(self.buttons_frame)
        self.buttons_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.open_camera_button = self.create_button("Ouvrir Webcam", self.start_camera)
        self.buttons.append(self.open_camera_button)
        self.close_camera_button = self.create_button("Fermer Webcam", self.stop_camera)
        self.buttons.append(self.close_camera_button)
        self.fullscreen_button = self.create_button("Plein Écran", self.toggle_camera_size)
        self.buttons.append(self.fullscreen_button)
        self.file_button = self.create_button("Sélectionner Fichier YAML", self.select_training_file)
        self.buttons.append(self.file_button)
        self.recognize_button = self.create_button("Démarrer Reconnaissance", self.toggle_reconnaissance)
        self.recognize_button.setEnabled(False)
        self.buttons.append(self.recognize_button)
        self.mainwindow_button = self.create_button("MainWindow", self.back_to_login_main_window)
        self.buttons.append(self.mainwindow_button)

        for button in self.buttons:
            self.buttons_layout.addWidget(button)
        self.buttons_layout.addStretch(1)

        main_layout.addWidget(self.buttons_frame)

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
            self.buttons_frame.hide()
            self.menu_bar.show()
            self.options_menu.clear()
            for button in self.buttons:
                action = QAction(button.text(), self)
                action.triggered.connect(button.clicked)
                self.options_menu.addAction(action)
        else:
            self.buttons_frame.show()
            self.menu_bar.hide()

    def create_button(self, text, callback=None):
        button = QPushButton(text)
        button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        if callback:
            button.clicked.connect(callback)
        return button

    def start_camera(self):
        if not self.webcam or not self.webcam.isOpened():
            self.webcam = cv2.VideoCapture(0)
            if not self.webcam.isOpened():
                QMessageBox.critical(self, "Erreur", "Impossible d'ouvrir la webcam.")
                return
        self.timer.start(30)

    def stop_camera(self):
        if self.webcam and self.webcam.isOpened():
            self.timer.stop()
            self.webcam.release()
            self.webcam = None
            self.webcam_label.clear()

    def update_frame(self):
        if self.webcam and self.webcam.isOpened():
            success, frame = self.webcam.read()
            if success:
                if self.is_recognizing and self.face_cascade and self.recognizer and self.training_file:
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(30, 30))

                    for (x, y, w, h) in faces:
                        face_roi = gray[y:y+h, x:x+w]
                        if face_roi.size == 0:
                            continue

                        try:
                            chauffeur_id, confidence = self.recognizer.predict(face_roi)
                            confidence_percent = 100 - int(confidence)
                            threshold = 60

                            if confidence_percent > threshold:
                                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                                cv2.putText(frame, f"ID: {chauffeur_id} ({confidence_percent}%)", (x, y - 10), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 127), 2)
                            else:
                                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                                cv2.putText(frame, "Inconnu", (x, y - 10), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 255), 2)

                        except Exception as e:
                            print(f"Erreur lors de la prédiction: {e}")
                            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                            cv2.putText(frame, "Erreur Prediction", (x, y - 10), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 255), 2)

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

    def toggle_camera_size(self):
        if not self.is_maximized:
            self.showFullScreen()
            self.is_maximized = True
        else:
            self.showNormal()
            self.is_maximized = False

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
                QMessageBox.information(self, "Succès", f"Fichier chargé: {os.path.basename(self.training_file)}")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement du fichier: {e}")
                self.training_file = None
                self.recognize_button.setEnabled(False)

    def toggle_reconnaissance(self):
        if not self.webcam or not self.webcam.isOpened():
            QMessageBox.warning(self, "Avertissement", "Veuillez d'abord démarrer la webcam.")
            return

        if not self.training_file:
            QMessageBox.warning(self, "Avertissement", "Veuillez sélectionner un fichier YAML d'entraînement.")
            return

        self.is_recognizing = not self.is_recognizing
        if self.is_recognizing:
            self.recognize_button.setText("Arrêter Reconnaissance")
            self.file_button.setEnabled(False)
        else:
            self.recognize_button.setText("Démarrer Reconnaissance")
            self.file_button.setEnabled(True)


