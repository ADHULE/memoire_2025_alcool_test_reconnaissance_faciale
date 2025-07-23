from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QLabel, QLineEdit, QPushButton,
    QCheckBox, QListWidget, QListWidgetItem, QMessageBox, QComboBox,
    QHBoxLayout
)
from PySide6.QtCore import *
from PySide6.QtGui import QIcon
import logging
from Controllers.administrateur_controller import ADMINISTRATEUR_CONTROLLER

class ENREGISTREMENT_ADMIN(QWidget):
    open_modify_page_signal = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestion des Administrateurs")
        self.parent = parent
        self.admin_controller = ADMINISTRATEUR_CONTROLLER()

        self.fields_creation = {
            "Nom d'utilisateur": QLineEdit(),
            "Mot de passe": QLineEdit(),
            "Rôle": QComboBox(),
            "Super Admin": QCheckBox("Super Admin"),
            "Actif": QCheckBox("Actif")
        }

        self.fields_creation["Mot de passe"].setEchoMode(QLineEdit.Password)
        self.fields_creation["Rôle"].addItems(["admin", "éditeur", "invité"])

        self.show_password_checkbox = QCheckBox("Afficher le mot de passe")
        self.enregistrer_button = QPushButton("Enregistrer")
        self.list_view = QListWidget()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher par nom...")
        self.refresh_button = QPushButton("Rafraîchir")

        self._build_ui()
        self._load_administrateurs()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Gestion des Administrateurs", alignment=Qt.AlignCenter))

        form_layout = QGridLayout()
        for i, (label, widget) in enumerate(self.fields_creation.items()):
            form_layout.addWidget(QLabel(f"{label}:"), i, 0)
            form_layout.addWidget(widget, i, 1)

        form_layout.addWidget(self.show_password_checkbox, len(self.fields_creation), 1)
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
        password_field = self.fields_creation["Mot de passe"]
        password_field.setEchoMode(QLineEdit.Normal if self.show_password_checkbox.isChecked() else QLineEdit.Password)

    def _enregistrer_administrateur(self):
        username = self.fields_creation["Nom d'utilisateur"].text().strip()
        password = self.fields_creation["Mot de passe"].text().strip()
        role = self.fields_creation["Rôle"].currentText()
        super_admin = self.fields_creation["Super Admin"].isChecked()
        is_active = self.fields_creation["Actif"].isChecked()

        if not username or len(username) < 3:
            self._show_message("Erreur", "Le nom d'utilisateur doit contenir au moins 3 caractères.")
            return
        if not password or len(password) < 6:
            self._show_message("Erreur", "Le mot de passe doit contenir au moins 6 caractères.")
            return

        try:
            admin = self.admin_controller.new_administrateur(
                username=username,
                password=password,
                role=role,
                is_active=is_active,
                super_admin=super_admin
            )
            if admin:
                self._show_message("Succès", "Administrateur enregistré avec succès.")
                self._load_administrateurs()
                for field in self.fields_creation.values():
                    if isinstance(field, QLineEdit):
                        field.clear()
                    elif isinstance(field, QCheckBox):
                        field.setChecked(False)
                self.fields_creation["Rôle"].setCurrentIndex(0)
            else:
                self._show_message("Erreur", "Échec de l'enregistrement.")
        except Exception as e:
            logging.error(f"Erreur d'enregistrement : {str(e)}")
            self._show_message("Erreur", f"Erreur d'enregistrement : {str(e)}")

    def _load_administrateurs(self):
        self.list_view.clear()
        try:
            administrateurs = self.admin_controller.get_all_administrateurs()
            for admin in administrateurs:
                statut = "Actif" if admin.is_active else "Inactif"
                privilege = "Super Admin" if admin.super_admin else "Standard"

                widget_item = QWidget()
                item_layout = QHBoxLayout(widget_item)

                # Libellé de l'administrateur
                label = QLabel(f"{admin.username} | {admin.role} | {statut} | {privilege}")

                # Bouton Modifier avec texte et icône
                btn_modifier = QPushButton("Modifier")
                btn_modifier.setIcon(QIcon("edit.png"))
                btn_modifier.setIconSize(QSize(16, 16))
                btn_modifier.setToolTip("Modifier cet administrateur")
                btn_modifier.clicked.connect(self._modify_admin, admin.id)

                # Bouton Supprimer avec texte et icône
                btn_supprimer = QPushButton("Supprimer")
                btn_supprimer.setIcon(QIcon("delete.png"))
                btn_supprimer.setIconSize(QSize(16, 16))
                btn_supprimer.setToolTip("Supprimer cet administrateur")
                btn_supprimer.clicked.connect(lambda checked, id=admin.id: self._delete_administrateur(id))

                # Ajouter tous les éléments à l'item layout
                item_layout.addWidget(label)
                item_layout.addWidget(btn_modifier)
                item_layout.addWidget(btn_supprimer)
                item_layout.setContentsMargins(5, 5, 5, 5)
                widget_item.setLayout(item_layout)

                # Ajouter l'item dans la liste
                item = QListWidgetItem(self.list_view)
                item.setSizeHint(widget_item.sizeHint())
                self.list_view.addItem(item)
                self.list_view.setItemWidget(item, widget_item)

        except Exception as e:
            logging.error(f"Erreur chargement : {str(e)}")
            self._show_message("Erreur", f"Erreur de chargement : {str(e)}")

    def _modify_admin(self, admin_id):
        try:
            if self.parent and hasattr(self.parent, "open_modify_admin_page"):
                self.parent.open_modify_admin_page(admin_id)
            else:
                self._show_message("Erreur", "La fenêtre principale ne définit pas la méthode 'open_modify_admin_page'.")
        except Exception as e:
            self._show_message("Erreur", f"Erreur lors de la modification : {str(e)}")

    def _delete_administrateur(self, admin_id):
        reply = QMessageBox.question(self, "Confirmation", "Supprimer cet administrateur ?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                self.admin_controller.delete_administrateur(admin_id)
                self._show_message("Succès", "Administrateur supprimé.")
                self._load_administrateurs()
            except Exception as e:
                logging.error(f"Erreur suppression : {str(e)}")
                self._show_message("Erreur", f"Erreur de suppression : {str(e)}")

    def _filter_administrateur(self):
        search_text = self.search_input.text().strip().lower()
        try:
            filtered = self.admin_controller.filter_administrateurs(username=search_text)
            self.list_view.clear()
            for admin in filtered:
                statut = "Actif" if admin.is_active else "Inactif"
                privilege = "Super Admin" if admin.super_admin else "Standard"

                widget_item = QWidget()
                item_layout = QHBoxLayout(widget_item)

                label = QLabel(f"{admin.username} | {admin.role} | {statut} | {privilege}")

                btn_modifier = QPushButton("Modifier")
                btn_modifier.setIcon(QIcon("edit.png"))
                btn_modifier.setToolTip("Modifier")
                btn_modifier.clicked.connect(lambda checked, id=admin.id: self.open_modify_page_signal.emit(id))

                btn_supprimer = QPushButton("Supprimer")
                btn_supprimer.setIcon(QIcon("delete.png"))
                btn_supprimer.setToolTip("Supprimer")
                btn_supprimer.clicked.connect(lambda checked, id=admin.id: self._delete_administrateur(id))

                item_layout.addWidget(label)
                item_layout.addWidget(btn_modifier)
                item_layout.addWidget(btn_supprimer)
                item_layout.setContentsMargins(5, 5, 5, 5)

                widget_item.setLayout(item_layout)

                item = QListWidgetItem(self.list_view)
                item.setSizeHint(widget_item.sizeHint())
                self.list_view.addItem(item)
                self.list_view.setItemWidget(item, widget_item)
        except Exception as e:
            logging.error(f"Erreur filtrage : {str(e)}")
            self._show_message("Erreur", f"Erreur de filtrage : {str(e)}")

    def _show_message(self, title, message):
        QMessageBox.information(self, title, message)
