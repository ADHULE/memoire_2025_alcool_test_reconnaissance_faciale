import os
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QImage, QPixmap, QFont, QIcon
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QComboBox, QLineEdit, QMessageBox, QFrame, QSizePolicy
)

from Controllers.arduino_controller import ArduinoController
from Controllers.camera_controller import CameraController
from Controllers.chauffeur_controller import CHAUFFEUR_CONTROLLER
from Controllers.historique_controller import HISTORIQUE_CONTROLLER
from Controllers.image_controller import IMAGE_CONTROLLER


class FACE_RECOGNITION_CAMERA(QMainWindow):
    """
    Fenêtre principale pour la reconnaissance faciale avec gestion
    des caméras locales et IP via OpenCV et PySide6.
    """
    mainwindow_signal = Signal()

    def __init__(self, person_controller=None, image_controller=None, history_controller=None, arduino_controller=None):
        super().__init__()
        self.setWindowTitle("LA RECONNAISSANCE FACIALE")

        # Initialisation de la source caméra active
        self.camera_source_active = None

        # Création des instances locales de contrôleurs
        self.person_controller = person_controller
        self.image_controller = image_controller
        self.arduino_controller = arduino_controller
        self.history_controller = history_controller

        # Création du CameraController
        self.camera_controller = CameraController(
            self.person_controller,
            self.image_controller,
            self.history_controller,
            self.arduino_controller
        )

        # Connexion des signaux
        self.camera_controller.frame_ready.connect(self.display_frame)
        self.camera_controller.error_occurred.connect(self.show_error)
        self.camera_controller.recognized.connect(self.log_recognition)

        # Construction de l’interface graphique
        self._setup_ui()

        # Chargement de la base des visages connus
        self.camera_controller.load_face_database()

    # -----------------------------
    # Gestion UI et caméra
    # -----------------------------
    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_h_layout = QHBoxLayout(central_widget)
        main_h_layout.setContentsMargins(10, 10, 10, 10)
        main_h_layout.setSpacing(15)

        # Panneau gauche
        control_panel = QFrame()
        control_panel.setFixedWidth(250)
        control_layout = QVBoxLayout(control_panel)
        control_layout.setContentsMargins(15, 15, 15, 15)
        control_layout.setSpacing(10)

        title_label = QLabel("Contrôles Caméra")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        control_layout.addWidget(title_label)
        control_layout.addSpacing(20)

        # URL caméra IP
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("URL de la caméra IP")
        control_layout.addWidget(self.url_input)
        self.connect_url_button = QPushButton("Activer l'Url")
        self.connect_url_button.clicked.connect(self._handle_url_connection)
        control_layout.addWidget(self.connect_url_button)
        control_layout.addSpacing(15)

        # Caméra locale
        self.cam_selector = QComboBox()
        self.cam_selector.addItems(self.camera_controller.detect_local_cameras())
        control_layout.addWidget(self.cam_selector)
        self.connect_local_button = QPushButton("Activer la caméra")
        self.connect_local_button.clicked.connect(self._handle_local_camera)
        control_layout.addWidget(self.connect_local_button)
        control_layout.addSpacing(15)

        # Arrêt caméra
        self.stop_button = QPushButton("Arrêter la caméra")
        self.stop_button.clicked.connect(self._handle_stop)
        control_layout.addWidget(self.stop_button)
        control_layout.addSpacing(15)

        # Plein écran
        self.fullscreen_button = QPushButton("Plein écran")
        self.fullscreen_button.clicked.connect(self._toggle_fullscreen)
        control_layout.addWidget(self.fullscreen_button)
        control_layout.addSpacing(20)

        # Icônes statut
        icon_display_layout = QHBoxLayout()
        icon_display_layout.setAlignment(Qt.AlignCenter)
        self.icon_label_1 = QLabel()
        self.icon_label_1.setPixmap(QPixmap("icons/status_idle_icon.png").scaled(48, 48))
        icon_display_layout.addWidget(self.icon_label_1)
        self.icon_label_2 = QLabel()
        self.icon_label_2.setPixmap(QPixmap("icons/recognition_idle_icon.png").scaled(48, 48))
        icon_display_layout.addWidget(self.icon_label_2)
        control_layout.addLayout(icon_display_layout)
        control_layout.addStretch()
        main_h_layout.addWidget(control_panel)

        # Zone vidéo
        video_frame = QFrame()
        video_layout = QVBoxLayout(video_frame)
        video_layout.setContentsMargins(10, 10, 10, 10)
        self.label_video = QLabel("Flux vidéo")
        self.label_video.setAlignment(Qt.AlignCenter)
        self.label_video.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.label_video.setScaledContents(True)
        self.label_video.setFont(QFont("Arial", 24, QFont.Bold))
        video_layout.addWidget(self.label_video)
        main_h_layout.addWidget(video_frame)

        self.fullscreen = False

    # -----------------------------
    # Gestion caméras
    # -----------------------------
    def _handle_local_camera(self):
        try:
            selection = self.cam_selector.currentText()
            if self.camera_source_active and self.camera_source_active != "locale":
                self.camera_controller.stop_camera()
            success = self.camera_controller.start_camera(selection)
            if success:
                self.camera_source_active = "locale"
                self.icon_label_1.setPixmap(QPixmap("icons/status_connected_icon.png").scaled(48, 48))
            else:
                self.label_video.setText("Impossible de connecter la caméra locale")
        except Exception as e:
            QMessageBox.warning(self, "Erreur", f"Caméra locale invalide : {e}")

    def _handle_url_connection(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Erreur", "Veuillez entrer une URL valide.")
            return
        if self.camera_source_active and self.camera_source_active != "url":
            self.camera_controller.stop_camera()
        success = self.camera_controller.start_camera_from_url(url)
        if success:
            self.camera_source_active = "url"
            self.url_input.setText("Connecté")
            self.icon_label_1.setPixmap(QPixmap("icons/status_connected_icon.png").scaled(48, 48))
        else:
            self.label_video.setText("Impossible de capturer le flux IP")

    def _handle_stop(self):
        self.camera_controller.stop_camera()
        self.label_video.setText("Flux vidéo")
        self.url_input.setText("")
        self.icon_label_1.setPixmap(QPixmap("icons/status_idle_icon.png").scaled(48, 48))
        self.icon_label_2.setPixmap(QPixmap("icons/recognition_idle_icon.png").scaled(48, 48))

    def _toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.showFullScreen()
            self.fullscreen_button.setText("Quitter plein écran")
        else:
            self.showNormal()
            self.fullscreen_button.setText("Plein écran")

    # -----------------------------
    # Affichage vidéo
    # -----------------------------
    def display_frame(self, frame):
        if frame is None:
            self.label_video.setText("Flux vidéo indisponible")
            return
        try:
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            qimg = QImage(frame.data, w, h, bytes_per_line, QImage.Format_BGR888)
            self.label_video.setPixmap(QPixmap.fromImage(qimg))
            self.icon_label_2.setPixmap(QPixmap("icons/recognition_active_icon.png").scaled(48, 48))
        except Exception as e:
            print(f"Erreur affichage frame : {e}")
            self.label_video.setText("Erreur affichage vidéo")

    def show_error(self, message):
        QMessageBox.critical(self, "Erreur", message)
        self.icon_label_1.setPixmap(QPixmap("icons/status_error_icon.png").scaled(48, 48))

    def log_recognition(self, name, score):
        print(f"✅ Reconnaissance : {name} avec un score de {score:.4f}")
