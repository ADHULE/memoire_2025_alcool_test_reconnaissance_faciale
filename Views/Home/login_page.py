import sys
from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, Signal


class LOGINWINDOW(QMainWindow):
    # Signal pour naviguer vers la page principale après la connexion
    home_page_signal = Signal()
    webcam_page_signal = Signal()
    # Signal pour gérer l'annulation de connexion
    cancel_signal = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Page de Connexion")

        # Création du widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal
        main_layout = QHBoxLayout(central_widget)

        # Partie gauche : Connexion
        left_layout = QVBoxLayout()
        left_layout.setSpacing(10)
        left_layout.addWidget(self._create_title_section())
        left_layout.addWidget(self._create_form_section())
        left_layout.addWidget(self._create_button_section())
        left_layout.addStretch()
        main_layout.addWidget(self.create_frame(left_layout), 1)

        # Partie droite : Accès à la caméra
        right_layout = QVBoxLayout()
        right_layout.setSpacing(10)
        right_layout.addWidget(self._create_camera_button())
        right_layout.addStretch()
        main_layout.addWidget(self.create_frame(right_layout), 1)

        # Chargement de la feuille de style
        self.load_stylesheet("Styles/login_styles.css")

    def _create_title_section(self) -> QFrame:
        """Crée la section titre."""
        title_layout = QHBoxLayout()
        title = QLabel("Connexion")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        title_layout.addWidget(title)
        return self.create_frame(title_layout)

    def _create_form_section(self) -> QFrame:
        """Crée la section de saisie du nom d'utilisateur et du mot de passe."""
        form_layout = QVBoxLayout()
        form_layout.addWidget(self.create_label("Nom d'utilisateur:"))
        self.username_lineedit = self.create_line_edit("Entrez votre nom d'utilisateur")
        form_layout.addWidget(self.username_lineedit)
        form_layout.addWidget(self.create_label("Mot de passe:"))
        self.password_lineedit = self.create_line_edit("Entrez votre mot de passe", password_mode=True)
        form_layout.addWidget(self.password_lineedit)
        return self.create_frame(form_layout)

    def _create_button_section(self) -> QFrame:
        """Crée la section contenant les boutons Connexion et Annuler."""
        button_layout = QHBoxLayout()
        login_button = self.create_button("Connexion", self.check_connexion)
        cancel_button = self.create_button("Annuler", self.cancel_login)
        button_layout.addWidget(login_button)
        button_layout.addWidget(cancel_button)
        return self.create_frame(button_layout)

    def _create_camera_button(self) -> QFrame:
        """Crée la section contenant le bouton d'accès à la caméra."""
        camera_layout = QVBoxLayout()
        btn_start_camera = self.create_button("Acceder a la page de commera", self.webcam_page)
        camera_layout.addWidget(btn_start_camera)
        camera_layout.addStretch()
        return self.create_frame(camera_layout)

    def create_label(self, text: str) -> QLabel:
        """Crée un label simple."""
        label = QLabel(text)
        label.setStyleSheet("font-size: 14px;")
        return label

    def create_line_edit(self, placeholder: str = "", password_mode: bool = False) -> QLineEdit:
        """Crée un champ de texte avec un texte indicatif et mode mot de passe."""
        line_edit = QLineEdit()
        line_edit.setPlaceholderText(placeholder)
        if password_mode:
            line_edit.setEchoMode(QLineEdit.EchoMode.Password)
        return line_edit

    def create_button(self, text: str, callback=None) -> QPushButton:
        """Crée un bouton et le relie à une action."""
        button = QPushButton(text)
        if callback:
            button.clicked.connect(callback)
        return button

    def create_frame(self, layout: QLayout) -> QFrame:
        """Crée un QFrame et lui assigne le layout donné."""
        frame = QFrame()
        frame.setObjectName("forme_frame")
        frame.setLayout(layout)
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setFrameShadow(QFrame.Raised)
        frame.setLineWidth(1)
        return frame

    def check_connexion(self) -> None:
        """Vérifie les informations de connexion et émet un signal."""
        # username = self.username_lineedit.text().strip()
        # password = self.password_lineedit.text().strip()
        # if username and password:
        self.home_page_signal.emit()
        self.close()
        # else:
        #     QMessageBox.warning(self, "Erreur", "Veuillez remplir tous les champs.")

    def cancel_login(self) -> None:
        """Émet un signal pour annuler la connexion."""
        self.cancel_signal.emit()

    def webcam_page(self):
        """Émet un signal pour ouvrir la page de la caméra."""
        self.webcam_page_signal.emit()

    def load_stylesheet(self, path: str) -> None:
        """Charge une feuille de style CSS depuis un fichier."""
        try:
            with open(path, "r") as file:
                self.setStyleSheet(file.read())
        except FileNotFoundError:
            QMessageBox.warning(self, "Erreur", f"Feuille de style non trouvée : {path}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur Critique", f"Impossible de charger la feuille de style : {e}")

