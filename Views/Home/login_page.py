
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QFrame, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QMessageBox, QCheckBox, QComboBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from Controllers.arduino_controller import ArduinoController


class LOGINWINDOW(QMainWindow):
    # Signaux personnalisés
    home_page_signal = Signal()
    webcam_page_signal = Signal()
    cancel_signal = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Connexion")
        self._load_stylesheet("Styles/login_styles.css")
        self._setup_ui()

        # Initialisation du contrôleur Arduino après la création des widgets GUI
        self.arduino_controller = ArduinoController(self.port_combobox, self.status_label)
        # self.arduino_value()
    def _load_stylesheet(self, path: str):
        """Charge une feuille de style CSS."""
        try:
            with open(path, "r") as file:
                self.setStyleSheet(file.read())
        except FileNotFoundError:
            QMessageBox.warning(self, "Erreur", f"Feuille de style non trouvée : {path}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de charger la feuille de style : {e}")

    def _setup_ui(self):
        """Configure l'ensemble de l'interface utilisateur."""
        self.main_frame = QWidget(self)
        self.setCentralWidget(self.main_frame)
        self.main_layout = QVBoxLayout(self.main_frame)

        general_frame = QFrame()
        general_frame.setObjectName("general_frame")
        general_layout = QVBoxLayout(general_frame)

        sections_frame = QFrame()
        sections_layout = QHBoxLayout(sections_frame)

        # Section Connexion
        login_section = self._create_section(
            "Images/login_image.jpeg",
            "Connexion",
            self._create_login_form(),
            [("Connexion", self._check_login), ("Annuler", self._cancel_login)]
        )

        # Section Arduino
        arduino_section = self._create_section(
            "Images/arduino_image.jpeg",
            "Arduino",
            self._create_arduino_content(),
            [("Actualiser", lambda: self.arduino_controller.detect_serial_ports()),
             ("Connecter", lambda: self.arduino_controller.connect_to_arduino())]
        )

        # Section Webcam
        camera_section = self._create_section(
            "Images/camera.jpg",
            "Caméra",
            None,
            [("Accéder à la caméra", self.webcam_page)]
        )

        # Ajout des sections
        sections_layout.addWidget(login_section)
        sections_layout.addWidget(arduino_section)
        sections_layout.addWidget(camera_section)

        general_layout.addWidget(sections_frame)
        self.main_layout.addWidget(general_frame)

    def _create_section(self, image_path, title, content_widget, buttons):
        """Crée une section de l'interface avec une image, un titre, du contenu et des boutons."""
        section_frame = QFrame()
        section_frame.setObjectName("section_frame")
        layout = QVBoxLayout(section_frame)

        if image_path:
            pixmap = QPixmap(image_path).scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            image_label = QLabel()
            image_label.setPixmap(pixmap)
            image_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(image_label)

        if title:
            title_label = QLabel(title)
            title_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(title_label)

        if content_widget:
            layout.addWidget(content_widget)

        button_frame = QFrame()
        button_layout = QHBoxLayout(button_frame)
        for text, function in buttons:
            button = self._create_button(text, function)
            button_layout.addWidget(button)
        layout.addWidget(button_frame)

        return section_frame

    def _create_button(self, text, function):
        """Crée un bouton avec une fonction liée."""
        button = QPushButton(text)
        button.setObjectName("button")
        button.clicked.connect(function)
        return button

    def _create_line_edit(self, placeholder_text: object = "", echo_mode: object = QLineEdit.EchoMode.Normal) -> QLineEdit:
        """Crée un champ de saisie de texte."""
        line_edit = QLineEdit()
        line_edit.setPlaceholderText(placeholder_text)
        line_edit.setEchoMode(echo_mode)
        return line_edit

    def _create_login_form(self):
        """Crée le formulaire de connexion."""
        form_frame = QFrame()
        form_frame.setObjectName("form_frame")
        layout = QVBoxLayout(form_frame)

        layout.addWidget(QLabel("Nom d'utilisateur :"))
        self.username_line_edit = self._create_line_edit("Entrez votre nom")
        layout.addWidget(self.username_line_edit)

        layout.addWidget(QLabel("Mot de passe :"))
        self.password_line_edit = self._create_line_edit("", QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_line_edit)

        self.show_password_check_box = QCheckBox("Afficher le mot de passe")
        self.show_password_check_box.stateChanged.connect(self._toggle_password_visibility)
        layout.addWidget(self.show_password_check_box)

        return form_frame

    def _create_arduino_content(self):
        """Crée les widgets nécessaires pour gérer Arduino."""
        frame = QFrame()
        frame.setObjectName("arduino_frame")
        layout = QVBoxLayout(frame)

        layout.addWidget(QLabel("Ports disponibles :"))
        self.port_combobox = QComboBox()
        layout.addWidget(self.port_combobox)

        self.status_label = QLabel("🔴 Déconnecté")
        self.status_label.setStyleSheet("font-weight: bold; color: red;")
        layout.addWidget(self.status_label)

        return frame

    def _toggle_password_visibility(self):
        """Affiche ou masque le mot de passe."""
        visible = self.show_password_check_box.isChecked()
        self.password_line_edit.setEchoMode(QLineEdit.EchoMode.Normal if visible else QLineEdit.EchoMode.Password)

    def _check_login(self):
        """Action de connexion simulée."""
        self.home_page_signal.emit()
        self.close()

    def _cancel_login(self):
        """Annule la tentative de connexion."""
        self.cancel_signal.emit()

    def webcam_page(self):
        """Émet un signal pour accéder à la webcam."""
        self.webcam_page_signal.emit()

    def arduino_value(self):
        """
        Affiche la valeur lue depuis l'Arduino dans une boîte de dialogue.
        """
        data = self.arduino_controller.read_data()
        if data:
            QMessageBox.information(self, "Valeur Arduino", f"Donnée reçue : {data}")
        else:
            QMessageBox.warning(self, "Aucune donnée", "Aucune donnée disponible à lire depuis Arduino.")

        # self.arduino_controller.data_received.connect(self.update_display)
