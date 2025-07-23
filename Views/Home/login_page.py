# Importation des composants PySide6 nécessaires pour l'interface graphique
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QFrame, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QMessageBox, QCheckBox, QComboBox
)


# Déclaration de la classe principale pour la fenêtre de connexion
class LOGINWINDOW(QMainWindow):
    # Définition de signaux personnalisés pour la navigation entre pages ou actions spécifiques
    home_page_signal = Signal()
    webcam_page_signal = Signal()
    cancel_signal = Signal()
    arduino_value_signal = Signal()

    def __init__(self, arduino_controller, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Connexion")
        self.arduino_controller = arduino_controller

        # Chargement de la feuille de style CSS
        self._load_stylesheet("Styles/login_styles.css")

        # Construction de l'interface utilisateur
        self._setup_ui()

        # Lier les composants de l'interface avec le contrôleur Arduino
        self.arduino_controller.port_combobox = self.port_combobox
        self.arduino_controller.status_label = self.status_label
        self.arduino_controller.connection_status_changed.connect(self._status_label_update)

        # Charge une feuille de style CSS externe.

    def _load_stylesheet(self, path: str):
        try:
            with open(path, "r") as file:
                self.setStyleSheet(file.read())
        except FileNotFoundError:
            QMessageBox.warning(self, "Erreur", f"Feuille de style non trouvée : {path}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de charger la feuille de style : {e}")

    # Construit le layout principal et les différentes sections (login, arduino, webcam).
    def _setup_ui(self):
        self.main_frame = QWidget(self)
        self.setCentralWidget(self.main_frame)
        self.main_layout = QVBoxLayout(self.main_frame)

        general_frame = QFrame()
        general_frame.setObjectName("general_frame")
        general_layout = QVBoxLayout(general_frame)
        sections_frame = QFrame()
        sections_frame.setObjectName("sections_frame")
        sections_layout = QHBoxLayout(sections_frame)
        # Section connexion utilisateur
        login_section = self._create_section(
            "Images/login_image.jpeg", "",
            self._create_login_form(),
            [("Connexion", self._check_login), ("Annuler", self._cancel_login)]
        )

        # Section Arduino : ports disponibles et connexion
        arduino_section = self._create_section(
            "Images/arduino_image.jpeg", "",
            self._create_arduino_content(),
            [("Actualiser", lambda: self.arduino_controller.detect_serial_ports()),
             ("Connecter", lambda: self.arduino_controller.connect_to_arduino()),
             ("Deconnecter", lambda: self.arduino_controller.close_connection()),
             ]
        )

        # Section Caméra : simple bouton pour accéder
        camera_section = self._create_section(
            "Images/camera.jpg", "", None,
            [("Accéder à la caméra", self.webcam_page)]
        )

        # Agencement des sections horizontalement avec des espaces
        sections_layout.addWidget(login_section)
        sections_layout.addStretch()
        sections_layout.addWidget(arduino_section)
        sections_layout.addStretch()
        sections_layout.addWidget(camera_section)

        general_layout.addWidget(sections_frame)
        self.main_layout.addWidget(general_frame)

    # Crée dynamiquement une section visuelle avec une image, un titre, un contenu et des boutons.
    def _create_section(self, image_path, title, content_widget, buttons):
        section_frame = QFrame()
        layout = QVBoxLayout(section_frame)

        # Affichage de l'image
        if image_path:
            pixmap = QPixmap(image_path).scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            image_label = QLabel()
            image_label.setPixmap(pixmap)
            image_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(image_label)

        # Affichage du titre
        if title:
            title_label = QLabel(title)
            title_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(title_label)

        # Ajout du contenu central (formulaire, contrôles…)
        if content_widget:
            layout.addWidget(content_widget)

        # Ajout des boutons d'action
        button_frame = QFrame()
        button_layout = QHBoxLayout(button_frame)
        for text, function in buttons:
            button = self._create_button(text, function)
            button_layout.addWidget(button)
        layout.addWidget(button_frame)

        return section_frame

    # Construit le formulaire de connexion avec champs utilisateur et mot de passe.
    def _create_login_form(self):
        form_frame = QFrame()
        layout = QVBoxLayout(form_frame)

        layout.addWidget(QLabel("Nom d'utilisateur :"))
        self.username_line_edit = self._create_line_edit("Entrez votre nom")
        layout.addWidget(self.username_line_edit)

        layout.addWidget(QLabel("Mot de passe :"))
        self.password_line_edit = self._create_line_edit("", QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_line_edit)

        # Case à cocher pour afficher/masquer le mot de passe
        self.show_password_check_box = QCheckBox("Afficher le mot de passe")
        self.show_password_check_box.stateChanged.connect(self._toggle_password_visibility)
        layout.addWidget(self.show_password_check_box)

        return form_frame

    # Crée les éléments d'interface liés à l’Arduino (combo des ports, état de connexion, bouton).
    def _create_arduino_content(self):
        frame = QFrame()
        layout = QVBoxLayout(frame)

        layout.addWidget(QLabel("Ports disponibles :"))
        self.port_combobox = QComboBox()
        layout.addWidget(self.port_combobox)

        # Étiquette d’état de connexion
        self.status_label = QLabel("🔴 Déconnecté")
        self.status_label.setStyleSheet("font-weight: bold; color: red;")

        # Bouton pour afficher une page liée aux valeurs Arduino
        self.btn_arduino_value = QPushButton("Arduino Value")
        self.btn_arduino_value.clicked.connect(self.go_to_arduno_value_page)

        # Mise en forme horizontale de l’étiquette et du bouton
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.status_label)
        self.layout.addWidget(self.btn_arduino_value)
        layout.addLayout(self.layout)

        return frame

    # Crée un bouton stylisé avec une fonction associée.
    def _create_button(self, text, function):
        button = QPushButton(text)
        button.setObjectName("button")
        button.clicked.connect(function)
        return button

    # Crée un champ de texte avec options de style et de visibilité.
    def _create_line_edit(self, placeholder_text="", echo_mode=QLineEdit.EchoMode.Normal):
        line_edit = QLineEdit()
        line_edit.setPlaceholderText(placeholder_text)
        line_edit.setEchoMode(echo_mode)
        return line_edit

    # Active ou désactive l'affichage du mot de passe selon l'état de la case à cocher.
    def _toggle_password_visibility(self):
        visible = self.show_password_check_box.isChecked()
        self.password_line_edit.setEchoMode(QLineEdit.EchoMode.Normal if visible else QLineEdit.EchoMode.Password)

    # Émet le signal pour accéder à la page d'accueil après connexion.
    def _check_login(self):
        self.home_page_signal.emit()
        self.close()

    # Émet le signal d’annulation (possiblement pour quitter ou réinitialiser l’interface).
    def _cancel_login(self):
        self.cancel_signal.emit()

    # Émet le signal pour basculer vers la page de la webcam.
    def webcam_page(self):
        self.webcam_page_signal.emit()

    # Met à jour l’indicateur de statut de l’Arduino en fonction de la connexion.
    def _status_label_update(self, connected: bool):
        if connected:
            self.status_label.setText("🟢 Connecté")
            self.status_label.setStyleSheet("font-weight: bold; color: green;")
        else:
            self.status_label.setText("🔴 Déconnecté")
            self.status_label.setStyleSheet("font-weight: bold; color: red;")

    # Émet le signal pour afficher les valeurs lues depuis l’Arduino.
    def go_to_arduno_value_page(self):
        self.arduino_value_signal.emit()
