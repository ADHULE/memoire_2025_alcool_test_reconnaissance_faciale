from PySide6.QtWidgets import *
from PySide6.QtCore import *
import re
from datetime import datetime
from Controllers.administrateur_controller import ADMINISTRATEUR_CONTROLLER

class ENREGISTREMENT_ADMIN(QWidget):
    open_modify_page_signal = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestion des Administrateurs")
        self.parent = parent
        self.admin_controller = ADMINISTRATEUR_CONTROLLER()
        
        self.fields = {name: QLineEdit() for name in ["Nom", "Post-Nom", "Prénom", "Téléphone", "Email", "Nom d'utilisateur", "Mot de passe", "Rôle"]}
        self.is_active_checkbox, self.super_admin_checkbox = QCheckBox("Actif"), QCheckBox("Super Admin")
        self.enregistrer_button = QPushButton("Enregistrer")
        self.list_view = QListWidget()
        self.search_input = QLineEdit(placeholderText="Rechercher...")
        self.refresh_button = QPushButton("Rafraîchir")

        self._build_ui()
        self._load_administrateurs()
        self.list_view.itemSelectionChanged.connect(self._on_item_selection_changed)
        self.open_modify_page_signal.connect(self._open_modify_page)

    def _build_ui(self):
        """Construit l'interface utilisateur simplifiée."""
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Gestion des Administrateurs", alignment=Qt.AlignCenter))

        form_layout = QGridLayout()
        for i, (label, field) in enumerate(self.fields.items()):
            field.setEchoMode(QLineEdit.Password if label == "Mot de passe" else QLineEdit.Normal)
            form_layout.addWidget(QLabel(f"{label}:"), i, 0)
            form_layout.addWidget(field, i, 1)

        form_layout.addWidget(self.is_active_checkbox, len(self.fields), 0)
        form_layout.addWidget(self.super_admin_checkbox, len(self.fields), 1)
        layout.addLayout(form_layout)

        self.enregistrer_button.clicked.connect(self._enregistrer_administrateur)
        layout.addWidget(self.enregistrer_button)

        self.search_input.textChanged.connect(self._filter_administrateur)
        layout.addWidget(self.search_input)
        layout.addWidget(self.list_view)
        self.refresh_button.clicked.connect(self._load_administrateurs)
        layout.addWidget(self.refresh_button)

    def _show_message(self, title, message):
        QMessageBox.information(self, title, message)

    def _load_administrateurs(self):
        """Charge les administrateurs et les affiche avec leurs boutons Modifier et Supprimer."""
        self.list_view.clear()
        try:
            for admin in self.admin_controller.get_all_administrateurs():
                widget_item = QWidget()
                item_layout = QHBoxLayout(widget_item)

                item_label = QLabel(f"{admin.nom} {admin.postnom}, {admin.prenom} ({admin.username})")
                modifier_button = QPushButton("Modifier")
                supprimer_button = QPushButton("Supprimer")

                modifier_button.clicked.connect(lambda checked, admin_id=admin.id: self._open_modify_page(admin_id))
                supprimer_button.clicked.connect(lambda checked, admin_id=admin.id: self._delete_administrateur_confirmation(admin_id))

                item_layout.addWidget(item_label)
                item_layout.addWidget(modifier_button)
                item_layout.addWidget(supprimer_button)
                item_layout.setContentsMargins(5, 5, 5, 5)

                item = QListWidgetItem()
                item.setSizeHint(widget_item.sizeHint())
                item.setData(Qt.UserRole, admin.id)
                self.list_view.addItem(item)
                self.list_view.setItemWidget(item, widget_item)
        except Exception as e:
            self._show_message("Erreur", f"Erreur de chargement : {str(e)}")

    def _filter_administrateur(self):
        """Filtre la liste des administrateurs en fonction du texte recherché."""
        search_text = self.search_input.text().strip().lower()
        for i in range(self.list_view.count()):
            item = self.list_view.item(i)
            item_widget = self.list_view.itemWidget(item)
            item_widget.setVisible(search_text in item_widget.findChild(QLabel).text().lower())

    def _on_item_selection_changed(self):
        """Gère le changement de sélection et affiche les boutons Modifier et Supprimer."""
        selected_items = self.list_view.selectedItems()
        for i in range(self.list_view.count()):
            item = self.list_view.item(i)
            item_widget = self.list_view.itemWidget(item)
            if item in selected_items:
                item_widget.findChild(QPushButton, "Modifier").setVisible(True)
                item_widget.findChild(QPushButton, "Supprimer").setVisible(True)
            else:
                item_widget.findChild(QPushButton, "Modifier").setVisible(False)
                item_widget.findChild(QPushButton, "Supprimer").setVisible(False)

    def _open_modify_page(self, admin_id):
        """Ouvre une nouvelle fenêtre pour modifier un administrateur."""
        self.parent.open_modify_admin_page(admin_id)

    def _delete_administrateur_confirmation(self, admin_id):
        """Confirme la suppression d'un administrateur."""
        if QMessageBox.question(self, "Confirmation", "Voulez-vous supprimer cet administrateur ?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self._delete_administrateur(admin_id)

    def _delete_administrateur(self, admin_id):
        """Supprime un administrateur."""
        try:
            if self.admin_controller.delete_administrateur(admin_id):
                self._show_message("Succès", "Administrateur supprimé avec succès.")
                self._load_administrateurs()
            else:
                self._show_message("Erreur", "Erreur lors de la suppression.")
        except Exception as e:
            self._show_message("Erreur", f"Erreur de suppression : {str(e)}")

    def _enregistrer_administrateur(self):
        """Enregistre un nouvel administrateur après validation."""
        data = {key: field.text().strip() for key, field in self.fields.items()}
        if not all(data.values()):
            self._show_message("Erreur", "Tous les champs doivent être remplis.")
            return
        if not data["Téléphone"].isdigit():
            self._show_message("Erreur", "Le téléphone doit contenir uniquement des chiffres.")
            return
        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", data["Email"]):
            self._show_message("Erreur", "Email invalide.")
            return

        now = datetime.now()
        data.update({"created_at": now.isoformat(), "last_login": now.isoformat(), "is_active": self.is_active_checkbox.isChecked(), "super_admin": self.super_admin_checkbox.isChecked()})

        if self.admin_controller.new_administrateur(**data):
            self._show_message("Succès", "Administrateur enregistré avec succès.")
            self._load_administrateurs()
        else:
            self._show_message("Erreur", "Erreur lors de l'enregistrement.")
