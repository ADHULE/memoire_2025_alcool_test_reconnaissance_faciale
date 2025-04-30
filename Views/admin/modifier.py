from PySide6.QtWidgets import *
from PySide6.QtCore import *
import re
from datetime import datetime
from Controllers.administrateur_controller import ADMINISTRATEUR_CONTROLLER

class MODIFIER_ADMIN(QDialog):
    def __init__(self, admin_id, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Modifier Administrateur")
        self.admin_id, self.admin_controller = admin_id, ADMINISTRATEUR_CONTROLLER()
        self.parent = parent

        # Création des champs avec les noms corrects
        self.fields = {
            "nom": QLineEdit(),
            "postnom": QLineEdit(),
            "prenom": QLineEdit(),
            "telephone": QLineEdit(),
            "email": QLineEdit(),
            "username": QLineEdit(),
            "role": QLineEdit()
        }
        self.is_active_checkbox, self.super_admin_checkbox = QCheckBox("Actif"), QCheckBox("Super Admin")

        # Construction UI
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Modifier Administrateur", alignment=Qt.AlignCenter))
        
        form_layout = QGridLayout()
        for i, (key, field) in enumerate(self.fields.items()):
            form_layout.addWidget(QLabel(f"{key.capitalize()}:"), i, 0)
            form_layout.addWidget(field, i, 1)

        form_layout.addWidget(self.is_active_checkbox, len(self.fields), 0)
        form_layout.addWidget(self.super_admin_checkbox, len(self.fields), 1)
        layout.addLayout(form_layout)

        # Boutons
        btn_layout = QHBoxLayout()
        btn_modifier = QPushButton("Modifier", clicked=self._modifier_administrateur)
        btn_annuler = QPushButton("Annuler", clicked=self.close)
        btn_layout.addWidget(btn_modifier)
        btn_layout.addWidget(btn_annuler)
        layout.addLayout(btn_layout)

        self._load_admin_data()

    def _show_message(self, title, message):
        QMessageBox.information(self, title, message)

    def _get_field_values(self):
        """Récupère les valeurs des champs."""
        return {key: field.text().strip() for key, field in self.fields.items()}

    def _load_admin_data(self):
        """Charge les données de l'administrateur."""
        try:
            admin = self.admin_controller.get_administrateur_by_id(self.admin_id)
            if admin:
                for key, field in self.fields.items():
                    field.setText(str(getattr(admin, key, "")))  # Utilisation directe des attributs sans espaces
                self.is_active_checkbox.setChecked(admin.is_active)
                self.super_admin_checkbox.setChecked(admin.super_admin)
            else:
                self._show_message("Erreur", "Administrateur non trouvé.")
                self.close()
        except Exception as e:
            self._show_message("Erreur", f"Erreur de chargement : {str(e)}")
            self.close()

    def _modifier_administrateur(self):
        """Modifie un administrateur existant après validation."""
        data = self._get_field_values()
        if not all(data.values()):
            self._show_message("Erreur", "Tous les champs doivent être remplis.")
            return
        if not data["telephone"].isdigit():
            self._show_message("Erreur", "Le téléphone doit contenir uniquement des chiffres.")
            return
        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", data["email"]):
            self._show_message("Erreur", "Email invalide.")
            return

        data.update({"admin_id": self.admin_id, "is_active": self.is_active_checkbox.isChecked(), "super_admin": self.super_admin_checkbox.isChecked()})

        if self.admin_controller.update_administrateur(**data):
            self._show_message("Succès", "Administrateur mis à jour avec succès.")
            if self.parent:
                self.parent._load_administrateurs()
            self.close()
        else:
            self._show_message("Erreur", "Erreur lors de la mise à jour.")
