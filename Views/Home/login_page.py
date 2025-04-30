import sys
from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap


class LOGINWINDOW(QMainWindow):
    home_page_signal = Signal()
    webcam_page_signal = Signal()
    cancel_signal = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Connexion")
        self.setMinimumSize(400, 300)

        # 🔹 Ajout de la feuille de style CSS
        self.load_stylesheet("Styles/login_styles.css")

        # 🏠 Conteneur principal
        main_frame = QFrame(self)
        main_frame.setObjectName("main_frame")  # 🔹 Identification CSS
        self.setCentralWidget(main_frame)
        main_layout = QVBoxLayout(main_frame)

        # 🏠 Ajout du conteneur de contenu
        content_frame = QFrame()
        content_frame.setObjectName("content_frame")  # 🔹 Identification CSS
        main_layout.addWidget(content_frame)

        # 📌 Layout principal : Division en 2 colonnes
        layout = QHBoxLayout(content_frame)

        # 🔹 Section Connexion (Gauche)
        left_layout = QVBoxLayout()
        left_layout.addWidget(self._create_image_section("Images/user_icon.png"))
        left_layout.addWidget(self._create_form_section())
        left_layout.addWidget(self._create_button_section())
        layout.addLayout(left_layout)

        # 🔹 Section Caméra (Droite)
        right_layout = QVBoxLayout()
        right_layout.addWidget(self._create_image_section("Images/camera.jpg"))
        right_layout.addWidget(self._create_camera_button())
        layout.addLayout(right_layout)

    def load_stylesheet(self, path: str):
        """🔹 Charge la feuille de style CSS depuis un fichier."""
        try:
            with open(path, "r") as file:
                self.setStyleSheet(file.read())
        except FileNotFoundError:
            QMessageBox.warning(
                self, "Erreur", f"Feuille de style non trouvée : {path}"
            )
        except Exception as e:
            QMessageBox.critical(
                self, "Erreur", f"Impossible de charger la feuille de style : {e}"
            )

    def _create_image_section(self, image_path: str) -> QLabel:
        """🔹 Ajoute une image en haut de chaque section."""
        image_label = QLabel()
        image_label.setPixmap(QPixmap(image_path).scaled(120, 120, Qt.KeepAspectRatio))
        image_label.setObjectName("image_section")
        image_label.setAlignment(Qt.AlignCenter)
        return image_label

    def _create_form_section(self) -> QFrame:
        form_layout = QVBoxLayout()
        form_layout.addWidget(QLabel("Nom d'utilisateur:"))
        self.username_lineedit = QLineEdit()
        form_layout.addWidget(self.username_lineedit)

        form_layout.addWidget(QLabel("Mot de passe:"))
        self.password_lineedit = QLineEdit()
        self.password_lineedit.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addWidget(self.password_lineedit)

        # 🔹 Ajout de la case à cocher pour afficher le mot de passe
        self.show_password_checkbox = QCheckBox("Afficher le mot de passe")
        self.show_password_checkbox.stateChanged.connect(
            self.toggle_password_visibility
        )
        form_layout.addWidget(self.show_password_checkbox)

        return self.create_frame(form_layout)

    def _create_button_section(self) -> QFrame:
        button_layout = QHBoxLayout()
        login_button = QPushButton("Connexion")
        cancel_button = QPushButton("Annuler")

        login_button.clicked.connect(self.check_connexion)
        cancel_button.clicked.connect(self.cancel_login)

        button_layout.addWidget(login_button)
        button_layout.addWidget(cancel_button)
        return self.create_frame(button_layout)

    def _create_camera_button(self) -> QFrame:
        camera_layout = QVBoxLayout()
        btn_camera = QPushButton("Accéder à la caméra")
        btn_camera.clicked.connect(self.webcam_page)

        camera_layout.addWidget(btn_camera)
        return self.create_frame(camera_layout)

    def create_frame(self, layout: QLayout) -> QFrame:
        frame = QFrame()
        frame.setObjectName(
            "section_frame"
        )  # 🔹 Identification CSS pour une meilleure apparence
        frame.setLayout(layout)
        return frame

    def toggle_password_visibility(self):
        """🔹 Affiche ou masque le mot de passe."""
        self.password_lineedit.setEchoMode(
            QLineEdit.EchoMode.Normal
            if self.show_password_checkbox.isChecked()
            else QLineEdit.EchoMode.Password
        )

    def check_connexion(self):
        self.home_page_signal.emit()
        self.close()

    def cancel_login(self):
        self.cancel_signal.emit()

    def webcam_page(self):
        self.webcam_page_signal.emit()
