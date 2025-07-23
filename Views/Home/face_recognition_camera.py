from PySide6.QtWidgets import (
    QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QComboBox, QLineEdit, QMessageBox
)
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt, Signal

from Controllers.camera_controller import CameraController
from Controllers.chauffeur_controller import CHAUFFEUR_CONTROLLER
from Controllers.image_controller import IMAGE_CONTROLLER
from Controllers.arduino_controller import ArduinoController


class   FACE_RECOGNITION_CAMERA(QMainWindow):
    mainwindow_signal = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("GESTION DE LA RECONNAISSANCE FACIALE")

        # Contrôleurs
        self.person_controller = CHAUFFEUR_CONTROLLER()
        self.image_controller = IMAGE_CONTROLLER()
        self.arduino_controller = ArduinoController()
        self.camera_controller = CameraController(self.person_controller, self.image_controller,self.arduino_controller)

        # Connexions aux signaux de logique
        self.camera_controller.frame_ready.connect(self.display_frame)
        self.camera_controller.error_occurred.connect(self.show_error)
        self.camera_controller.recognized.connect(self.log_recognition)

        self._setup_ui()
        self.camera_controller.load_face_database()

    def _setup_ui(self):
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        self.label_video = QLabel("Flux vidéo")
        self.label_video.setAlignment(Qt.AlignCenter)
        self.label_video.setScaledContents(True)
        layout.addWidget(self.label_video)

        controls = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("URL de la caméra IP (ex: http://.../video)")
        controls.addWidget(self.url_input)
        # controls.addStretch()

        self.connect_url_button = QPushButton("Activer URL")
        self.connect_url_button.clicked.connect(self._handle_url_connection)
        controls.addWidget(self.connect_url_button)
        controls.addStretch()

        self.cam_selector = QComboBox()
        self.cam_selector.addItems(self.camera_controller.detect_local_cameras())
        controls.addWidget(self.cam_selector)
        controls.addStretch()

        self.connect_local_button = QPushButton("Activer Webcam")
        self.connect_local_button.clicked.connect(self._handle_local_camera)
        controls.addWidget(self.connect_local_button)
        controls.addStretch()

        self.stop_button = QPushButton("Arrêter")
        self.stop_button.clicked.connect(self._handle_stop)
        controls.addWidget(self.stop_button)
        controls.addStretch()

        self.fullscreen_button = QPushButton("Plein écran")
        self.fullscreen_button.clicked.connect(self._toggle_fullscreen)
        controls.addWidget(self.fullscreen_button)
        controls.addStretch()

        layout.addLayout(controls)
        self.setCentralWidget(central_widget)

        self.fullscreen = False

    def _handle_url_connection(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Erreur", "Veuillez entrer une URL valide.")
            return
        success = self.camera_controller.start_camera(url)
        if success:
            self.url_input.setText("Connecté")

    def _handle_local_camera(self):
        try:
            index = int(self.cam_selector.currentText().split()[-1])
            self.camera_controller.start_camera(index)
        except Exception:
            QMessageBox.warning(self, "Erreur", "Caméra sélectionnée invalide.")

    def _handle_stop(self):
        self.camera_controller.stop_camera()
        self.label_video.clear()
        self.url_input.setText("")

    def _toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.showFullScreen()
            self.fullscreen_button.setText("Quitter plein écran")
        else:
            self.showNormal()
            self.fullscreen_button.setText("Plein écran")

    def display_frame(self, frame):
        h, w, ch = frame.shape
        qimg = QImage(frame.data, w, h, ch * w, QImage.Format_BGR888)
        self.label_video.setPixmap(QPixmap.fromImage(qimg))

    def show_error(self, message):
        QMessageBox.critical(self, "Erreur", message)

    def log_recognition(self, name, score):
        print(f"Reconnaissance : {name} avec un score de {score:.4f}")
