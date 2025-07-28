from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QBitmap, QPainter
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QFrame, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QMessageBox, QCheckBox, QComboBox
)


class LOGINWINDOW(QMainWindow):
    home_page_signal = Signal()
    webcam_page_signal = Signal()
    cancel_signal = Signal()
    arduino_value_signal = Signal()

    def __init__(self, arduino_controller, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Connexion")
        self.arduino_controller = arduino_controller

        self._load_stylesheet("Styles/login_styles.css")
        self._setup_ui()

        self.arduino_controller.port_combobox = self.port_combobox
        self.arduino_controller.status_label = self.status_label
        self.arduino_controller.connection_status_changed.connect(self._status_label_update)

    def _load_stylesheet(self, path: str):
        try:
            with open(path, "r") as file:
                self.setStyleSheet(file.read())
        except FileNotFoundError:
            QMessageBox.warning(self, "Erreur", f"Feuille de style non trouvée : {path}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de charger la feuille de style : {e}")

    def _setup_ui(self):
        self.main_frame = QWidget(self)
        self.setCentralWidget(self.main_frame)
        self.main_layout = QVBoxLayout(self.main_frame)
        # self.main_layout.setContentsMargins(20, 20, 20, 20)

        general_frame = QFrame()
        general_frame.setObjectName("general_frame")
        general_layout = QVBoxLayout(general_frame)
        general_layout.setSpacing(20)

        sections_frame = QFrame()
        sections_frame.setObjectName("sections_frame")
        sections_layout = QHBoxLayout(sections_frame)
        sections_layout.setSpacing(30)
        # sections_layout.setContentsMargins(10, 10, 10, 10)

        # Section utilisateur - image moyenne
        login_section = self._create_section(
            "Images/login.png", "",
            self._create_login_form(),
            [("Connexion", self._check_login), ("Annuler", self._cancel_login)],
            image_size=(150, 150)
        )

        # Section Arduino - image plus petite
        arduino_section = self._create_section(
            "Images/arduino_circular_image.png", "",
            self._create_arduino_content(),
            [
                ("Actualiser", lambda: self.arduino_controller.detect_serial_ports()),
                ("Connecter", lambda: self.arduino_controller.connect_to_arduino()),
                ("Déconnecter", lambda: self.arduino_controller.close_connection())
            ],
            image_size=(300, 200)
        )

        # Section caméra - image plus large
        camera_section = self._create_section(
            "Images/circular_camera_image.png", "",
            None,
            [("Accéder à la caméra", self.webcam_page)],
            image_size=(300, 200)
        )

        # Ajout des sections
        sections_layout.addWidget(login_section, 1)
        sections_layout.addWidget(arduino_section, 1)
        sections_layout.addWidget(camera_section, 1)

        general_layout.addWidget(sections_frame)
        self.main_layout.addWidget(general_frame)

    def _create_section(self, image_path, title, content_widget, buttons, image_size=(200, 200)):
        section_frame = QFrame()
        layout = QVBoxLayout(section_frame)
        layout.setSpacing(10)

        if image_path:
            pixmap = QPixmap(image_path).scaled(image_size[0], image_size[1], Qt.KeepAspectRatio, Qt.SmoothTransformation)
            image_label = QLabel()
            image_label.setObjectName("section_image")
            image_label.setPixmap(pixmap)
            image_label.setPixmap(pixmap)
            image_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(image_label)
            # Masque pour arrondir les coins
            mask = QBitmap(pixmap.size())
            mask.clear()
            painter = QPainter(mask)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setBrush(Qt.white)
            painter.drawRoundedRect(0, 0, pixmap.width(), pixmap.height(), 25, 25)
            painter.end()

        if title:
            title_label = QLabel(title)
            title_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(title_label)

        if content_widget:
            layout.addWidget(content_widget)

        button_frame = QFrame()
        button_layout = QHBoxLayout(button_frame)
        button_layout.setSpacing(8)

        for text, function in buttons:
            button = self._create_button(text, function)
            button_layout.addWidget(button)

        layout.addWidget(button_frame)

        return section_frame

    def _create_login_form(self):
        form_frame = QFrame()
        layout = QVBoxLayout(form_frame)
        layout.setSpacing(8)

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
        frame = QFrame()
        layout = QVBoxLayout(frame)
        layout.setSpacing(8)

        layout.addWidget(QLabel("Ports disponibles :"))
        self.port_combobox = QComboBox()
        layout.addWidget(self.port_combobox)

        self.status_label = QLabel("Déconnecté")
        self.status_label.setStyleSheet("font-weight: bold; color: red;")

        self.btn_arduino_value = QPushButton("Arduino Value")
        self.btn_arduino_value.clicked.connect(self.go_to_arduno_value_page)

        status_layout = QHBoxLayout()
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.btn_arduino_value)

        layout.addLayout(status_layout)

        return frame

    def _create_button(self, text, function):
        button = QPushButton(text)
        button.setObjectName("button")
        button.clicked.connect(function)
        return button

    def _create_line_edit(self, placeholder_text="", echo_mode=QLineEdit.EchoMode.Normal):
        line_edit = QLineEdit()
        line_edit.setPlaceholderText(placeholder_text)
        line_edit.setEchoMode(echo_mode)
        return line_edit
    #     afficher le password ou hide
    def _toggle_password_visibility(self):
        visible = self.show_password_check_box.isChecked()
        self.password_line_edit.setEchoMode(QLineEdit.EchoMode.Normal if visible else QLineEdit.EchoMode.Password)

    def _check_login(self):
        self.home_page_signal.emit()
        self.close()

    def _cancel_login(self):
        self.cancel_signal.emit()

    def webcam_page(self):
        self.webcam_page_signal.emit()

    def _status_label_update(self, connected: bool):
        if connected:
            self.status_label.setText("Connecté")
            self.status_label.setStyleSheet("font-weight: bold; color: green;")
        else:
            self.status_label.setText("Déconnecté")
            self.status_label.setStyleSheet("font-weight: bold; color: red;")

    def go_to_arduno_value_page(self):
        self.arduino_value_signal.emit()
