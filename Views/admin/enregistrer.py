from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, Signal
import logging
from datetime import datetime
from Controllers.administrateur_controller import ADMINISTRATEUR_CONTROLLER

class ENREGISTREMENT_ADMIN(QWidget):
    open_modify_page_signal = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestion des Administrateurs")
        self.parent = parent
        self.admin_controller = ADMINISTRATEUR_CONTROLLER()

        self.fields_labels_creation = ["Nom d'utilisateur", "Mot de passe"]
        self.fields_creation = {name: QLineEdit() for name in self.fields_labels_creation}
        self.show_password_checkbox = QCheckBox("Afficher le mot de passe")
        self.enregistrer_button = QPushButton("Enregistrer")
        self.list_view = QListWidget()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher...")
        self.refresh_button = QPushButton("Rafraîchir")

        self._build_ui()
        self._load_administrateurs()

    def _build_ui(self):
        """Construit l'interface utilisateur."""
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Gestion des Administrateurs", alignment=Qt.AlignCenter))

        form_layout = QGridLayout()
        for i, label in enumerate(self.fields_labels_creation):
            field = self.fields_creation[label]
            if label == "Mot de passe":
                field.setEchoMode(QLineEdit.Password)
            form_layout.addWidget(QLabel(f"{label}:"), i, 0)
            form_layout.addWidget(field, i, 1)

        form_layout.addWidget(self.show_password_checkbox, len(self.fields_labels_creation), 1)
        self.show_password_checkbox.stateChanged.connect(self._toggle_password_visibility)

        layout.addLayout(form_layout)
        layout.addWidget(self.enregistrer_button)
        self.enregistrer_button.clicked.connect(self._enregistrer_administrateur)

        layout.addWidget(self.search_input)
        self.search_input.textChanged.connect(self._filter_administrateur)
        layout.addWidget(self.list_view)
        layout.addWidget(self.refresh_button)
        self.refresh_button.clicked.connect(self._load_administrateurs)

   
    def _toggle_password_visibility(self):
        """Affiche ou masque le mot de passe."""
        password_field = self.fields_creation["Mot de passe"]
        password_field.setEchoMode(QLineEdit.Normal if self.show_password_checkbox.isChecked() else QLineEdit.Password)
    def _enregistrer_administrateur(self):
        """Ajoute un nouvel administrateur après validation."""
        username = self.fields_creation["Nom d'utilisateur"].text().strip()
        password = self.fields_creation["Mot de passe"].text().strip()

        if not username or len(username) < 3:
            self._show_message("Erreur", "Le nom d'utilisateur doit contenir au moins 3 caractères.")
            return
        if not password or len(password) < 6:
            self._show_message("Erreur", "Le mot de passe doit contenir au moins 6 caractères.")
            return

        admin_data = {
            "username": username,
            "password": password,
            "created_at": datetime.now(),
            "last_login": None,
            "is_active": True,
            "super_admin": False
        }

        try:
            if self.admin_controller.new_administrateur(**admin_data):
                self._show_message("Succès", "Administrateur enregistré avec succès.")
                self._load_administrateurs()
                for field in self.fields_creation.values():
                    field.clear()
                self.show_password_checkbox.setChecked(False)
            else:
                self._show_message("Erreur", "Échec de l'enregistrement.")
        except Exception as e:
            self._show_message("Erreur", f"Erreur d'enregistrement : {str(e)}")

    def _load_administrateurs(self):
        """Charge les administrateurs et les affiche."""
        self.list_view.clear()
        try:
            administrateurs = self.admin_controller.get_all_administrateurs()
            if not administrateurs:
                # self._show_message("Information", ".")
                return

            for admin in administrateurs:
                item = QListWidgetItem(f"{admin.username} ({'Actif' if admin.is_active else 'Inactif'})")
                item.setData(Qt.UserRole, admin.id)
                self.list_view.addItem(item)
        except Exception as e:
            self._show_message("Erreur", f"Erreur de chargement : {str(e)}")

    def _filter_administrateur(self):
        """Filtre les administrateurs selon le texte entré."""
        search_text = self.search_input.text().strip().lower()
        for i in range(self.list_view.count()):
            item = self.list_view.item(i)
            item.setHidden(search_text not in item.text().lower())

    def _show_message(self, title, message):
        """Affiche une boîte de dialogue informative."""
        QMessageBox.information(self, title, message)
