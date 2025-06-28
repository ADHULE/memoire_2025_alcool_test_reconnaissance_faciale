from PySide6.QtWidgets import *
from PySide6.QtCore import *
import re
from Controllers.chauffeur_controller import CHAUFFEUR_CONTROLLER

class MODIFIER_CHAUFFEUR(QDialog):
    def __init__(self, chauffeur_id, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Modifier Chauffeur")
        self.chauffeur_id = chauffeur_id
        self.chauffeur_controller = CHAUFFEUR_CONTROLLER()
        self.parent_widget = parent

        # Création des champs
        self.fields = {
            "nom": QLineEdit(),
            "postnom": QLineEdit(),
            "prenom": QLineEdit(),
            "telephone": QLineEdit(),
            "email": QLineEdit(),
            "numero_permis": QLineEdit(),
            "sex":QLineEdit(),
        }
        # Suppression du checkbox is_active

        # Interface utilisateur
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Modifier Chauffeur", alignment=Qt.AlignmentFlag.AlignCenter))

        form_layout = QGridLayout()
        for i, (key, field) in enumerate(self.fields.items()):
            form_layout.addWidget(QLabel(f"{key.replace('_', ' ').capitalize()}:"), i, 0)
            form_layout.addWidget(field, i, 1)

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
            chauffeur = self.chauffeur_controller.get_driver_by_id(self.chauffeur_id)
            if chauffeur:
                for key, field in self.fields.items():
                    if hasattr(chauffeur, key):
                        field.setText(str(getattr(chauffeur, key, "")))
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
        if not data["telephone"].isdigit():
            self._show_message("Erreur", "Le téléphone doit contenir uniquement des chiffres.")
            return
        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", data["email"]):
            self._show_message("Erreur", "Email invalide.")
            return

        data["chauffeur_id"] = self.chauffeur_id
        # Suppression de l'ajout de is_active au dictionnaire data

        if self.chauffeur_controller.update_driver(**data):
            self._show_message("Succès", "Chauffeur modifié avec succès.")
            if self.parent_widget and hasattr(self.parent_widget, '_load_chauffeurs'):
                self.parent_widget._load_chauffeurs()
            self.close()
        else:
            self._show_message("Erreur", "Erreur lors de la mise à jour.")
