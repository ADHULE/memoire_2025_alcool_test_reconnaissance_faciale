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
        self.setMinimumSize(800, 600)  # Interface responsive

        # Création du widget central et du layout principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Partie gauche : Connexion
        self.left_panel = QWidget()
        left_layout = QVBoxLayout(self.left_panel)
        left_layout.setSpacing(10)
        left_layout.addWidget(self.create_title_frame())
        left_layout.addWidget(self.create_form_frame())
        left_layout.addWidget(self.create_button_frame())
        left_layout.addStretch()

        # Partie droite : Accès à la caméra
        self.right_panel = QWidget()
        right_layout = QVBoxLayout(self.right_panel)
        right_layout.setSpacing(10)

        # Ajout du titre de la partie caméra
        camera_title = QLabel("Accès à la Caméra")
        camera_title.setAlignment(Qt.AlignCenter)
        camera_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        right_layout.addWidget(camera_title)

        # Ajout du bouton pour accéder à la caméra
        self.btn_start_camera = self.create_button("Ouvrir la caméra", self.webcam_page)
        right_layout.addWidget(self.btn_start_camera)

        right_layout.addStretch()

        self.right_panel.setLayout(right_layout)

        # Ajout des panneaux dans le layout principal
        main_layout.addWidget(self.left_panel, 1)
        main_layout.addWidget(self.right_panel, 1)

        # Chargement de la feuille de style
        self.load_stylesheet("Styles/login_styles.css")

    def create_title_frame(self) -> QFrame:
        """Crée la zone titre."""
        title_frame = QFrame()
        title_layout = QHBoxLayout(title_frame)

        title = QLabel("Connexion")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold;")

        title_layout.addWidget(title)
        return title_frame

    def create_form_frame(self) -> QFrame:
        """Crée la zone de saisie du nom d'utilisateur et du mot de passe."""
        form_frame = QFrame()
        form_layout = QVBoxLayout(form_frame)

        form_layout.addWidget(self.create_label("Nom d'utilisateur:"))
        self.username_lineedit = self.create_line_edit("Entrez votre nom d'utilisateur")
        form_layout.addWidget(self.username_lineedit)

        form_layout.addWidget(self.create_label("Mot de passe:"))
        self.password_lineedit = self.create_line_edit("Entrez votre mot de passe", password_mode=True)
        form_layout.addWidget(self.password_lineedit)

        return form_frame

    def create_button_frame(self) -> QFrame:
        """Crée la zone contenant les boutons Connexion et Annuler."""
        button_frame = QFrame()
        button_layout = QHBoxLayout(button_frame)
        login_button = self.create_button("Connexion", self.check_connexion)
        cancel_button = self.create_button("Annuler", self.cancel_login)
        button_layout.addWidget(login_button)
        button_layout.addWidget(cancel_button)
        return button_frame

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

    def check_connexion(self) -> None:
        """Vérifie les informations de connexion et émet un signal."""
        username = self.username_lineedit.text().strip()
        password = self.password_lineedit.text().strip()
        if username and password:
            self.home_page_signal.emit()
            self.close()
        else:
            QMessageBox.warning(self, "Erreur", "Veuillez remplir tous les champs.")

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

