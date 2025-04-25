import sys
from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, Signal
from functools import partial

class LoginWindow(QMainWindow):
    # Signal pour naviguer vers la page principale après la connexion
    home_page_signal = Signal()
    # Signal pour gérer l'annulation de connexion
    cancel_signal = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Page de Connexion")
        self.setMinimumSize(800, 600)  # Définition d'une taille minimale pour l'interface responsive

        # Création du widget central et d'un layout horizontal répartissant l'écran en deux parties
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Partie gauche : options de connexion
        self.left_panel = QWidget()
        left_layout = QVBoxLayout(self.left_panel)
        left_layout.setSpacing(10)  # Espacement pour une meilleure lisibilité
        left_layout.addWidget(self.create_title_frame())
        left_layout.addWidget(self.create_form_frame())
        left_layout.addWidget(self.create_button_frame())
        left_layout.addStretch()  # Pour occuper l'espace restant

        # Partie droite : boutons de contrôle de la caméra
        self.right_panel = QWidget()
        right_layout = QVBoxLayout(self.right_panel)
        right_layout.setSpacing(10)
        right_layout.addWidget(self.create_camera_control_frame())
        right_layout.addStretch()

        # Ajout des deux panneaux dans le layout principal avec le même facteur d'étirement
        main_layout.addWidget(self.left_panel, 1)
        main_layout.addWidget(self.right_panel, 1)

        # Chargement de la feuille de style (si le fichier existe)
        self.load_stylesheet("Styles/login_styles.css")

    def create_title_frame(self) -> QFrame:
        """
        Crée une zone titre avec un logo à gauche, un titre centré et un logo à droite.
        """
        title_frame = QFrame()
        title_frame.setObjectName("titleFrame")
        title_layout = QHBoxLayout(title_frame)

        left_logo = QLabel()
        left_logo.setObjectName("leftLogo")
        left_logo.setFixedSize(150, 150)

        title = QLabel("Connexion")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)

        right_logo = QLabel()
        right_logo.setObjectName("rightLogo")
        right_logo.setFixedSize(150, 150)

        title_layout.addWidget(left_logo)
        title_layout.addWidget(title)
        title_layout.addWidget(right_logo)
        return title_frame

    def create_form_frame(self) -> QFrame:
        """
        Crée la zone de saisie du nom d'utilisateur et du mot de passe.
        Remarque : les QLineEdit sont stockées dans les variables d'instance pour y accéder directement.
        """
        form_frame = QFrame()
        form_frame.setObjectName("formFrame")
        form_layout = QVBoxLayout(form_frame)

        # Saisie du nom d'utilisateur
        form_layout.addWidget(self.create_label("Nom d'utilisateur:"))
        self.username_lineedit = self.create_line_edit("Entrez votre nom d'utilisateur")
        self.username_lineedit.setObjectName("usernameLineEdit")
        form_layout.addWidget(self.username_lineedit)

        # Saisie du mot de passe et bouton pour basculer la visibilité
        form_layout.addWidget(self.create_label("Mot de passe:"))
        password_layout = QHBoxLayout()
        self.password_lineedit = self.create_line_edit("Entrez votre mot de passe", password_mode=True)
        self.password_lineedit.setObjectName("passwordLineEdit")
        password_toggle = self.create_button("👁", self.toggle_password_visibility)
        password_toggle.setFixedWidth(30)
        password_layout.addWidget(self.password_lineedit)
        password_layout.addWidget(password_toggle)
        form_layout.addLayout(password_layout)

        return form_frame

    def create_button_frame(self) -> QFrame:
        """
        Crée la zone contenant les boutons "Connexion" et "Annuler".
        """
        button_frame = QFrame()
        button_frame.setObjectName("buttonFrame")
        button_layout = QHBoxLayout(button_frame)
        button_layout.addStretch()
        login_button = self.create_button("Connexion", self.check_connexion)
        cancel_button = self.create_button("Annuler", self.cancel_login)
        button_layout.addWidget(login_button)
        button_layout.addStretch()
        button_layout.addWidget(cancel_button)
        button_layout.addStretch()
        return button_frame

    def create_camera_control_frame(self) -> QFrame:
        """
        Crée la zone de contrôle de la caméra qui se trouve dans la partie droite.
        Contient un titre et des boutons pour activer ou stopper la caméra.
        """
        camera_frame = QFrame()
        camera_frame.setObjectName("cameraFrame")
        camera_layout = QVBoxLayout(camera_frame)

        camera_label = self.create_label("Contrôle de la Caméra", font_size=16, bold=True, align_center=True)
        camera_layout.addWidget(camera_label)

        # Bouton pour activer la caméra
        self.btn_start_camera = self.create_button("Activer la Caméra", self.start_camera)
        # Bouton pour stopper la caméra, désactivé par défaut tant que la caméra n'est pas démarrée
        self.btn_stop_camera = self.create_button("Stop Caméra", self.stop_camera)
        self.btn_stop_camera.setEnabled(False)

        camera_layout.addWidget(self.btn_start_camera)
        camera_layout.addWidget(self.btn_stop_camera)
        camera_layout.addStretch()

        return camera_frame

    def create_label(self, text: str, font_size: int = 14, bold: bool = False, align_center: bool = False) -> QLabel:
        """
        Crée un QLabel avec des styles de base.
        """
        label = QLabel(text)
        label.setWordWrap(True)
        style = f"font-size: {font_size}px;"
        if bold:
            style += " font-weight: bold;"
        label.setStyleSheet(style)
        if align_center:
            label.setAlignment(Qt.AlignCenter)
        return label

    def create_line_edit(self, placeholder: str = "", password_mode: bool = False) -> QLineEdit:
        """
        Crée un QLineEdit avec un texte indicatif et un mode "mot de passe" optionnel.
        """
        line_edit = QLineEdit()
        line_edit.setPlaceholderText(placeholder)
        if password_mode:
            line_edit.setEchoMode(QLineEdit.EchoMode.Password)
        return line_edit

    def create_button(self, text: str, callback=None) -> QPushButton:
        """
        Crée un QPushButton et connecte le signal clicked à la méthode callback, si fournie.
        """
        button = QPushButton(text)
        if callback:
            button.clicked.connect(callback)
        return button

    def check_connexion(self) -> None:
        """
        Vérifie les informations de connexion et, en cas de succès, navigue vers la page principale.
        En cas d'erreur, affiche une boîte de dialogue d'avertissement.
        """
        username = self.username_lineedit.text().strip()
        password = self.password_lineedit.text().strip()
        # if not username or not password:
        #     QMessageBox.warning(self, "Erreur de connexion", "Veuillez remplir tous les champs.")
        #     return

        # # Exemple simplifié ; remplacez par une logique d'authentification réelle
        # if username == "admin" and password == "password":
        self.home_page_signal.emit()
        self.close()
        # else:
        #     QMessageBox.warning(self, "Erreur de connexion", "Nom d'utilisateur ou mot de passe incorrect.")

    def cancel_login(self) -> None:
        """
        Émet le signal d'annulation et permet d'effectuer d'éventuelles actions complémentaires.
        """
        self.cancel_signal.emit()

    def toggle_password_visibility(self) -> None:
        """
        Bascule le mode d'affichage du mot de passe pour le rendre visible ou masqué.
        """
        if self.password_lineedit.echoMode() == QLineEdit.EchoMode.Password:
            self.password_lineedit.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.password_lineedit.setEchoMode(QLineEdit.EchoMode.Password)

    def start_camera(self) -> None:
        """
        Active la page caméra. Dans cet exemple, on met à jour l'interface pour refléter l'état actif.
        """
        print("Camera activée...")
        self.btn_start_camera.setEnabled(False)
        self.btn_stop_camera.setEnabled(True)
        # Ici, vous pouvez ajouter la logique pour afficher la page ou lancer le flux de la caméra.

    def stop_camera(self) -> None:
        """
        Arrête la page caméra. On rétablit les boutons afin de permettre une nouvelle activation.
        """
        print("Camera arrêtée...")
        self.btn_start_camera.setEnabled(True)
        self.btn_stop_camera.setEnabled(False)
        # Ici, vous pouvez ajouter la logique pour stopper le flux de la caméra.

    def load_stylesheet(self, path: str) -> None:
        """
        Charge une feuille de style CSS depuis un fichier donné.
        """
        try:
            with open(path, "r") as file:
                self.setStyleSheet(file.read())
        except FileNotFoundError:
            QMessageBox.warning(self, "Erreur", f"Feuille de style non trouvée : {path}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur Critique", f"Impossible de charger la feuille de style : {e}")

