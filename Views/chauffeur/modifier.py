from PySide6.QtWidgets import *
from PySide6.QtCore import *
import re
from Controllers.chauffeur_controller import CHAUFFEUR_CONTROLLER

class MODIFIER_CHAUFFEUR(QDialog):
    def __init__(self, chauffeur_id, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Modifier Chauffeur")
        self.chauffeur_id, self.chauffeur_controller = chauffeur_id, CHAUFFEUR_CONTROLLER()
        self.parent = parent

        # Création des champs
        self.fields = {name: QLineEdit() for name in ["Nom", "Post-Nom", "Prénom", "Téléphone", "Email", "Numéro de permis"]}
        self.is_active_checkbox = QCheckBox("Actif")

        # Interface utilisateur
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Modifier Chauffeur", alignment=Qt.AlignCenter))

        form_layout = QGridLayout()
        for i, (key, field) in enumerate(self.fields.items()):
            form_layout.addWidget(QLabel(f"{key}:"), i, 0)
            form_layout.addWidget(field, i, 1)

        form_layout.addWidget(self.is_active_checkbox, len(self.fields), 1)
        layout.addLayout(form_layout)

        # Boutons
        btn_layout = QHBoxLayout()
        btn_modifier = QPushButton("Modifier", clicked=self._modifier_chauffeur)
        btn_annuler = QPushButton("Annuler", clicked=self.close)
        btn_layout.addWidget(btn_modifier)
        btn_layout.addWidget(btn_annuler)
        layout.addLayout(btn_layout)

        self._load_chauffeur_data()

    def _show_message(self, title, message):
        QMessageBox.information(self, title, message)

    def _get_field_values(self):
        """Récupère les valeurs des champs."""
        return {key: field.text().strip() for key, field in self.fields.items()}

    def _load_chauffeur_data(self):
        """Charge les données du chauffeur."""
        try:
            chauffeur = self.chauffeur_controller.get_driver(self.chauffeur_id)
            if chauffeur:
                for key, field in self.fields.items():
                    field.setText(str(getattr(chauffeur, key.replace(" ", "").lower(), "")))
                self.is_active_checkbox.setChecked(chauffeur.is_active)
            else:
                self._show_message("Erreur", "Chauffeur non trouvé.")
                self.close()
        except Exception as e:
            self._show_message("Erreur", f"Erreur de chargement : {str(e)}")
            self.close()

    def _modifier_chauffeur(self):
        """Modifie un chauffeur existant après validation."""
        data = self._get_field_values()
        if not all(data.values()):
            self._show_message("Erreur", "Tous les champs doivent être remplis.")
            return
        if not data["Téléphone"].isdigit():
            self._show_message("Erreur", "Le téléphone doit contenir uniquement des chiffres.")
            return
        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", data["Email"]):
            self._show_message("Erreur", "Email invalide.")
            return

        data.update({"chauffeur_id": self.chauffeur_id, "is_active": self.is_active_checkbox.isChecked()})

        if self.chauffeur_controller.update_driver(**data):
            self._show_message("Succès", "Chauffeur modifié avec succès.")
            if self.parent:
                self.parent._load_chauffeurs()
            self.close()
        else:
            self._show_message("Erreur", "Erreur lors de la mise à jour.")
