from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QGridLayout, QLabel, QLineEdit,
    QPushButton, QCheckBox, QMessageBox, QComboBox, QHBoxLayout
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
import re
from Controllers.administrateur_controller import ADMINISTRATEUR_CONTROLLER

class MODIFIER_ADMIN(QDialog):
    def __init__(self, username, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Modifier Administrateur")
        self.setWindowIcon(QIcon("edit_admin.png"))
        self.username = username
        self.admin_controller = ADMINISTRATEUR_CONTROLLER()
        self.parent = parent

        # Champs du formulaire
        self.username_field = QLineEdit()
        self.password_field = QLineEdit()
        self.password_field.setEchoMode(QLineEdit.Password)
        self.role_field = QComboBox()
        self.role_field.addItems(["admin", "éditeur", "invité"])

        self.show_password_checkbox = QCheckBox("Afficher le mot de passe")
        self.is_active_checkbox = QCheckBox("Actif")
        self.super_admin_checkbox = QCheckBox("Super Admin")

        # Mise en page
        layout = QVBoxLayout(self)


        form_layout = QGridLayout()
        form_layout.addWidget(QLabel("Nom d'utilisateur:"), 0, 0)
        form_layout.addWidget(self.username_field, 0, 1)

        form_layout.addWidget(QLabel("Mot de passe (laisser vide si inchangé):"), 1, 0)
        form_layout.addWidget(self.password_field, 1, 1)
        form_layout.addWidget(self.show_password_checkbox, 2, 1)
        self.show_password_checkbox.stateChanged.connect(self._toggle_password_visibility)

        form_layout.addWidget(QLabel("Rôle:"), 3, 0)
        form_layout.addWidget(self.role_field, 3, 1)

        form_layout.addWidget(self.is_active_checkbox, 4, 0)
        form_layout.addWidget(self.super_admin_checkbox, 4, 1)
        layout.addLayout(form_layout)

        # Boutons
        btn_layout = QHBoxLayout()
        btn_modifier = QPushButton("Enregistrer")
        btn_modifier.setIcon(QIcon("save.png"))
        btn_modifier.setIconSize(QSize(18, 18))
        btn_modifier.clicked.connect(self._modifier_administrateur)

        btn_annuler = QPushButton("Annuler")
        btn_annuler.setIcon(QIcon("cancel.png"))
        btn_annuler.setIconSize(QSize(18, 18))
        btn_annuler.clicked.connect(self.close)

        btn_layout.addWidget(btn_modifier)
        btn_layout.addWidget(btn_annuler)
        layout.addLayout(btn_layout)
        layout.addStretch()
        # Charger les données existantes
        self._load_admin_data()

    def _toggle_password_visibility(self):
        mode = QLineEdit.Normal if self.show_password_checkbox.isChecked() else QLineEdit.Password
        self.password_field.setEchoMode(mode)

    def _show_message(self, title, message):
        QMessageBox.information(self, title, message)

    def _load_admin_data(self):
        admin = self.admin_controller.get_administrateur_by_username(self.username)
        if admin:
            self.username_field.setText(admin.username)
            self.role_field.setCurrentText(admin.role)
            self.is_active_checkbox.setChecked(admin.is_active)
            self.super_admin_checkbox.setChecked(admin.super_admin)
        else:
            self._show_message("Erreur", "Administrateur introuvable.")
            self.close()

    def _modifier_administrateur(self):
        username = self.username_field.text().strip()
        role = self.role_field.currentText()
        password = self.password_field.text().strip()
        is_active = self.is_active_checkbox.isChecked()
        super_admin = self.super_admin_checkbox.isChecked()

        if not username or len(username) < 3:
            self._show_message("Erreur", "Le nom d'utilisateur doit contenir au moins 3 caractères.")
            return

        if password and len(password) < 6:
            self._show_message("Erreur", "Le mot de passe doit contenir au moins 6 caractères.")
            return

        reply = QMessageBox.question(self, "Confirmation", "Confirmer les modifications ?", QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return

        try:
            success = self.admin_controller.update_administrateur(
                admin_id=self.admin_id,
                username=username,
                password=password if password else None,
                role=role,
                is_active=is_active,
                super_admin=super_admin
            )
            if success:
                self._show_message("Succès", "Administrateur mis à jour avec succès.")
                if self.parent and hasattr(self.parent, "_load_administrateurs"):
                    self.parent._load_administrateurs()
                self.close()
            else:
                self._show_message("Erreur", "Échec de la mise à jour.")
        except Exception as e:
            self._show_message("Erreur", f"Exception : {str(e)}")
