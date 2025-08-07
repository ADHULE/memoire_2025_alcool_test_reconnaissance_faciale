from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QImage, QPixmap, QFont, QIcon
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QComboBox, QLineEdit, QMessageBox, QFrame, QSizePolicy
)

from Controllers.arduino_controller import ArduinoController
from Controllers.camera_controller import CameraController
from Controllers.chauffeur_controller import CHAUFFEUR_CONTROLLER
from Controllers.image_controller import IMAGE_CONTROLLER
from Controllers.historique_controller import HISTORIQUE_CONTROLLER

class FACE_RECOGNITION_CAMERA(QMainWindow):
    mainwindow_signal = Signal()

    def __init__(self, person_controller, image_controller, history_controller=None, arduino_controller=None):
        super().__init__()
        self.setWindowTitle("LA RECONNAISSANCE FACIALE")
        # self.resize(800, 600)

        # Contrôleurs
        self.person_controller = CHAUFFEUR_CONTROLLER()
        self.image_controller = IMAGE_CONTROLLER()
        self.arduino_controller = ArduinoController()
        self.history_controller = HISTORIQUE_CONTROLLER()
        self.camera_controller = CameraController( person_controller, image_controller, history_controller, arduino_controller)

        # Connexions aux signaux de logique
        self.camera_controller.frame_ready.connect(self.display_frame)
        self.camera_controller.error_occurred.connect(self.show_error)
        self.camera_controller.recognized.connect(self.log_recognition)

        self._setup_ui()
        self.camera_controller.load_face_database()

    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main horizontal layout to divide content (left panel + video feed)
        main_h_layout = QHBoxLayout(central_widget)
        main_h_layout.setContentsMargins(10, 10, 10, 10)
        main_h_layout.setSpacing(15)

        # --- Left Control Panel ---
        control_panel = QFrame()
        control_panel.setObjectName("controlPanel") # Object name for styling
        control_panel.setFrameShape(QFrame.StyledPanel)
        control_panel.setFrameShadow(QFrame.Raised)
        control_panel.setFixedWidth(250)

        control_layout = QVBoxLayout(control_panel)
        control_layout.setContentsMargins(15, 15, 15, 15)
        control_layout.setSpacing(10)

        # Title for the control panel
        title_label = QLabel("Contrôles Caméra")
        title_label.setObjectName("panelTitle") # Object name for styling
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        control_layout.addWidget(title_label)
        control_layout.addSpacing(20)

        # URL Input and Button
        url_section_layout = QVBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setObjectName("urlInput") # Object name for styling
        self.url_input.setPlaceholderText("URL de la caméra IP")
        url_section_layout.addWidget(self.url_input)

        self.connect_url_button = QPushButton("Activer l'Url")
        self.connect_url_button.setObjectName("connectUrlButton") # Object name for styling
        self.connect_url_button.setIcon(QIcon("icons/link_icon.png")) # Placeholder for icon
        self.connect_url_button.setIconSize(QSize(20, 20))
        self.connect_url_button.clicked.connect(self._handle_url_connection)
        url_section_layout.addWidget(self.connect_url_button)
        control_layout.addLayout(url_section_layout)
        control_layout.addSpacing(15)

        # Local Camera Selector and Button
        local_cam_section_layout = QVBoxLayout()
        self.cam_selector = QComboBox()
        self.cam_selector.setObjectName("camSelector") # Object name for styling
        self.cam_selector.addItems(self.camera_controller.detect_local_cameras())
        local_cam_section_layout.addWidget(self.cam_selector)

        self.connect_local_button = QPushButton("Activer la caméra")
        self.connect_local_button.setObjectName("connectLocalButton") # Object name for styling
        self.connect_local_button.setIcon(QIcon("icons/webcam_icon.png")) # Placeholder for icon
        self.connect_local_button.setIconSize(QSize(20, 20))
        self.connect_local_button.clicked.connect(self._handle_local_camera)
        local_cam_section_layout.addWidget(self.connect_local_button)
        control_layout.addLayout(local_cam_section_layout)
        control_layout.addSpacing(15)

        # Stop Button
        self.stop_button = QPushButton("Arrêter la caméra")
        self.stop_button.setObjectName("stopButton") # Object name for styling
        self.stop_button.setIcon(QIcon("icons/stop_icon.png")) # Placeholder for icon
        self.stop_button.setIconSize(QSize(20, 20))
        self.stop_button.clicked.connect(self._handle_stop)
        control_layout.addWidget(self.stop_button)
        control_layout.addSpacing(15)

        # Fullscreen Button
        self.fullscreen_button = QPushButton("Plein écran")
        self.fullscreen_button.setObjectName("fullscreenButton") # Object name for styling
        self.fullscreen_button.setIcon(QIcon("icons/fullscreen_icon.png")) # Placeholder for icon
        self.fullscreen_button.setIconSize(QSize(20, 20))
        self.fullscreen_button.clicked.connect(self._toggle_fullscreen)
        control_layout.addWidget(self.fullscreen_button)
        control_layout.addSpacing(20)

        # Placeholder for image icons (e.g., status indicators, branding)
        icon_display_layout = QHBoxLayout()
        icon_display_layout.setAlignment(Qt.AlignCenter)

        # Example Icon Placeholder 1
        self.icon_label_1 = QLabel()
        self.icon_label_1.setObjectName("statusIcon1") # Object name for styling
        self.icon_label_1.setPixmap(QPixmap("icons/status_idle_icon.png").scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)) # Placeholder icon
        self.icon_label_1.setToolTip("Statut de la connexion")
        icon_display_layout.addWidget(self.icon_label_1)

        icon_display_layout.addSpacing(15)

        # Example Icon Placeholder 2
        self.icon_label_2 = QLabel()
        self.icon_label_2.setObjectName("statusIcon2") # Object name for styling
        self.icon_label_2.setPixmap(QPixmap("icons/recognition_active_icon.png").scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)) # Placeholder icon
        self.icon_label_2.setToolTip("Statut de reconnaissance")
        icon_display_layout.addWidget(self.icon_label_2)

        control_layout.addLayout(icon_display_layout)

        # Add a stretch to push everything to the top
        control_layout.addStretch()
        main_h_layout.addWidget(control_panel)

        # --- Video Feed Area ---
        video_frame = QFrame()
        video_frame.setObjectName("videoFrame") # Object name for styling
        video_frame.setFrameShape(QFrame.StyledPanel)
        video_frame.setFrameShadow(QFrame.Raised)

        video_layout = QVBoxLayout(video_frame)
        video_layout.setContentsMargins(10, 10, 10, 10)

        self.label_video = QLabel("Flux vidéo")
        self.label_video.setObjectName("videoLabel") # Object name for styling
        self.label_video.setAlignment(Qt.AlignCenter)
        self.label_video.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.label_video.setScaledContents(True)
        self.label_video.setFont(QFont("Arial", 24, QFont.Bold))

        video_layout.addWidget(self.label_video)
        main_h_layout.addWidget(video_frame)

        self.fullscreen = False

    def _handle_url_connection(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Erreur", "Veuillez entrer une URL valide.")
            return
        success = self.camera_controller.start_camera(url)
        if success:
            self.url_input.setText("Connecté")
            self.icon_label_1.setPixmap(QPixmap("icons/status_connected_icon.png").scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)) # Update icon
        else:
            self.icon_label_1.setPixmap(QPixmap("icons/status_error_icon.png").scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)) # Update icon

    def _handle_local_camera(self):
        try:
            index = int(self.cam_selector.currentText().split()[-1])
            self.camera_controller.start_camera(index)
            self.icon_label_1.setPixmap(QPixmap("icons/status_connected_icon.png").scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)) # Update icon
        except Exception:
            QMessageBox.warning(self, "Erreur", "Caméra sélectionnée invalide.")
            self.icon_label_1.setPixmap(QPixmap("icons/status_error_icon.png").scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)) # Update icon

    def _handle_stop(self):
        self.camera_controller.stop_camera()
        self.label_video.clear()
        self.label_video.setText("Flux vidéo") # Reset text
        self.url_input.setText("")
        self.icon_label_1.setPixmap(QPixmap("icons/status_idle_icon.png").scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)) # Reset icon
        self.icon_label_2.setPixmap(QPixmap("icons/recognition_idle_icon.png").scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)) # Reset icon

    def _toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.showFullScreen()
            self.fullscreen_button.setText("Quitter plein écran")
            self.fullscreen_button.setIcon(QIcon("icons/exit_fullscreen_icon.png")) # Placeholder for icon
            self.fullscreen_button.setIconSize(QSize(20, 20))
        else:
            self.showNormal()
            self.fullscreen_button.setText("Plein écran")
            self.fullscreen_button.setIcon(QIcon("icons/fullscreen_icon.png")) # Placeholder for icon
            self.fullscreen_button.setIconSize(QSize(20, 20))

    def display_frame(self, frame):
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        qimg = QImage(frame.data, w, h, bytes_per_line, QImage.Format_BGR888)
        self.label_video.setPixmap(QPixmap.fromImage(qimg))
        self.icon_label_2.setPixmap(QPixmap("icons/recognition_active_icon.png").scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)) # Indicate active recognition

    def show_error(self, message):
        QMessageBox.critical(self, "Erreur", message)
        self.icon_label_1.setPixmap(QPixmap("icons/status_error_icon.png").scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)) # Update icon to error

    def log_recognition(self, name, score):
        print(f"Reconnaissance : {name} avec un score de {score:.4f}")


