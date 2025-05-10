import sys
import serial.tools.list_ports
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
        self._load_stylesheet("Styles/login_styles.css")
        self._setup_ui()

    def _load_stylesheet(self, path: str):
        """Charge la feuille de style CSS depuis un fichier."""
        try:
            with open(path, "r") as file:
                self.setStyleSheet(file.read())
        except FileNotFoundError:
            QMessageBox.warning(
                self, "Erreur", f"Feuille de style non trouvée : {path}")
        except Exception as e:
            QMessageBox.critical(
                self, "Erreur", f"Impossible de charger la feuille de style : {e}")

    def _setup_ui(self):
        """Configure l'interface utilisateur principale."""
        self.main_frame = QWidget(self)
        self.setCentralWidget(self.main_frame)
        self.main_layout = QVBoxLayout(self.main_frame)

        # Frame générale
        general_frame = QFrame()
        general_frame.setObjectName("general_frame")
        general_layout = QVBoxLayout(general_frame)

        sections_frame = QFrame()
        sections_layout = QHBoxLayout(sections_frame)

        sections_layout.addWidget(self._create_section("Images/login_image.jpeg", "Login", self._create_login_form(), [("Connexion", self._check_login), ("Annuler", self._cancel_login)]))
        sections_layout.addWidget(self._create_section("Images/arduino_image.jpeg", "Connexion Arduino", self._create_arduino_content(), [("Actualiser", self._detect_serial_ports), ("Connecter", self._connect_to_arduino)]))

        sections_layout.addWidget(self._create_section("Images/camera.jpg", "Caméra", None, [("Accéder à la caméra", self.webcam_page)]))

        general_layout.addWidget(sections_frame)
        self.main_layout.addWidget(general_frame)

    def _create_button(self, text, function):
        """Crée un bouton avec son action."""
        button = QPushButton(text)
        button.setObjectName("button")
        button.clicked.connect(function)
        return button

    def _create_section(self, image_path, title, content_widget, buttons):
        """Crée une section avec une image, un titre, un contenu, et ses propres boutons."""
        section_frame = QFrame()
        section_frame.setObjectName("section_frame")
        layout = QVBoxLayout(section_frame)

        if image_path:
            pixmap = QPixmap(image_path).scaled(
                120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            image_label = QLabel()
            image_label.setPixmap(pixmap)
            image_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(image_label)

        layout.addWidget(QLabel(title, alignment=Qt.AlignCenter))
        if content_widget:
            layout.addWidget(content_widget)

        button_frame = QFrame()
        button_layout = QHBoxLayout(button_frame)
        for text, function in buttons:
            button_layout.addWidget(self._create_button(text, function))

        layout.addWidget(button_frame)
        return section_frame

    def _create_login_form(self) -> QFrame:
        """Crée le formulaire de connexion."""
        form_frame = QFrame()
        form_frame.setObjectName("form_frame")
        layout = QVBoxLayout(form_frame)

        layout.addWidget(QLabel("Nom d'utilisateur:"))
        self.username_line_edit = self._create_line_edit()
        layout.addWidget(self.username_line_edit)

        layout.addWidget(QLabel("Mot de passe:"))
        self.password_line_edit = self._create_line_edit(
            echo_mode=QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_line_edit)

        self.show_password_check_box = QCheckBox("Afficher le mot de passe")
        self.show_password_check_box.stateChanged.connect(
            self._toggle_password_visibility)
        layout.addWidget(self.show_password_check_box)

        return form_frame

    def _create_line_edit(self, placeholder_text="", echo_mode=QLineEdit.EchoMode.Normal) -> QLineEdit:
        """Crée un champ de saisie avec un texte indicatif et un mode d'affichage spécifique."""
        line_edit = QLineEdit()
        line_edit.setPlaceholderText(placeholder_text)
        line_edit.setEchoMode(echo_mode)
        return line_edit

    def _create_arduino_content(self) -> QFrame:
        """Crée la section Arduino."""
        section_frame = QFrame()
        section_frame.setObjectName("arduino_frame")
        layout = QVBoxLayout(section_frame)

        layout.addWidget(QLabel("Connexion Arduino"))
        layout.addWidget(QLabel("Ports disponibles :"))
        self.port_combobox = QComboBox()
        layout.addWidget(self.port_combobox)

        self.status_label = QLabel("Statut : Non connecté")
        layout.addWidget(self.status_label)

        return section_frame

    def _toggle_password_visibility(self):
        """Affiche ou masque le mot de passe."""
        self.password_line_edit.setEchoMode(
            QLineEdit.EchoMode.Normal if self.show_password_check_box.isChecked() else QLineEdit.EchoMode.Password)

    def _detect_serial_ports(self):
        """Détecte et affiche les ports série disponibles."""
        self.port_combobox.clear()
        available_ports = serial.tools.list_ports.comports()
        for port_info in available_ports:
            self.port_combobox.addItem(
                f"{port_info.device} - {port_info.description}")
        if self.port_combobox.count() == 0:
            self.port_combobox.addItem("Aucun port série détecté")

    def _connect_to_arduino(self):
        """Connecte à Arduino."""
        selected_port_with_description = self.port_combobox.currentText()
        if " - " in selected_port_with_description:
            selected_port = selected_port_with_description.split(" - ")[0]
            try:
                with serial.Serial(selected_port, baudrate=9600, timeout=1) as arduino_serial:
                    self.status_label.setText(
                        f"Statut : Connecté à {selected_port}")
            except serial.SerialException:
                self.status_label.setText(
                    f"Statut : Erreur de connexion sur {selected_port}")

    def _check_login(self):
        """Vérifie la connexion et ferme la fenêtre."""
        self.home_page_signal.emit()
        self.close()

    def _cancel_login(self):
        """Annule la connexion."""
        self.cancel_signal.emit()

    def webcam_page(self):
        """Accède à la webcam."""
        self.webcam_page_signal.emit()
