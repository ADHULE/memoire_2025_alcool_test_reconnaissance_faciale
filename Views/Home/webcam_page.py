from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import QTimer, Qt, Signal
import sys
import cv2


class ACCER_WEBCAMERA(QMainWindow):
    # Déclaration correcte du signal pour la connexion à une autre interface
    login_page_signal = Signal()

    def __init__(self):
        super().__init__()

        self.setWindowTitle("ACCEDER A LA CAMERA")

        # Déterminer la taille maximale de l'écran
        self.screen = QApplication.primaryScreen().availableGeometry()
        self.is_maximized = False  # Variable pour gérer l'affichage plein écran

        # Initialisation de la webcam et du timer
        self.webcam = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        # Création des éléments de l'interface
        self.setup_ui()

    def setup_ui(self):
        """Configure l'interface avec uniquement la webcam et les boutons."""
        self.central_widget = QWidget()
        layout = QVBoxLayout(self.central_widget)

        # Label pour afficher la webcam
        self.webcam_label = QLabel(self)
        self.webcam_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.webcam_label.setScaledContents(False)  # Désactivé pour éviter les distorsions
        self.webcam_label.setStyleSheet("background-color: black;")  # Fond noir
        layout.addWidget(self.webcam_label)

        # Boutons pour gérer la webcam
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.create_button("Ouvrir Webcam", self.start_camera))
        btn_layout.addWidget(self.create_button("Fermer Webcam", self.stop_camera))
        btn_layout.addWidget(self.create_button("Plein Écran", self.toggle_camera_size))
        layout.addLayout(btn_layout)

        # Définir le widget central
        self.setCentralWidget(self.central_widget)
        self.load_stylesheet("Styles/webcam_style.css")  # Vérifiez que le fichier est au bon emplacement

    def create_button(self, text, callback=None):
        """Crée un bouton avec une action spécifique."""
        button = QPushButton(text)
        if callback:
            button.clicked.connect(callback)
        return button

    def start_camera(self):
        """Démarrer la webcam."""
        self.webcam = cv2.VideoCapture(0)
        if not self.webcam.isOpened():
            print("Erreur : Impossible d'ouvrir la webcam")
            return
        self.timer.start(30)  # Met à jour l'image toutes les 30ms

    def stop_camera(self):
        """Arrêter la webcam."""
        if self.webcam:
            self.timer.stop()
            self.webcam.release()
            self.webcam_label.clear()

    def update_frame(self):
        """Met à jour l'affichage de la webcam pour qu'elle s'adapte à la taille du label."""
        if self.webcam:
            success, frame = self.webcam.read()
            if success:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = frame.shape
                bytes_per_line = ch * w
                q_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)

                # Adapter la taille de l'image selon le QLabel
                scaled_image = q_image.scaled(
                    self.webcam_label.width(),
                    self.webcam_label.height(),
                    Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                    Qt.TransformationMode.SmoothTransformation,
                )
                self.webcam_label.setPixmap(QPixmap.fromImage(scaled_image))

    def toggle_camera_size(self):
        """Alterner entre la taille normale et le plein écran."""
        if not self.is_maximized:
            self.showFullScreen()
            self.is_maximized = True
        else:
            self.showNormal()
            self.is_maximized = False

    def load_stylesheet(self, path: str) -> None:
        """Charge une feuille de style CSS."""
        try:
            with open(path, "r") as file:
                self.setStyleSheet(file.read())
        except FileNotFoundError:
            QMessageBox.warning(self, "Erreur", f"Feuille de style non trouvée : {path}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur Critique", f"Impossible de charger la feuille de style : {e}")

    def back_to_login_page(self):
        """Émettre un signal pour revenir à la page de connexion."""
        self.login_page_signal.emit()


