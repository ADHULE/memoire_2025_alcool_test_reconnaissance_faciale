from PySide6.QtWidgets import *
# from PySide6.QtCore import *
from Controllers.chauffeur_controller import CHAUFFEUR_CONTROLLER
from functools import partial


class ENREGISTREMENT_CHAUFFEUR(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # self.setWindowTitle("Gestion des Chauffeurs")
        self.parent = parent
        self.chauffeur_controller = CHAUFFEUR_CONTROLLER()

        self.main_layout = QVBoxLayout(self)

        # Formulaire d'enregistrement
        self.form_group = QGroupBox("Ajouter les nouvelles informations")
        self.form_layout = QGridLayout()

        self.fields = {
            "Nom": QLineEdit(),
            "Post-Nom": QLineEdit(),
            "Prenom": QLineEdit(),
            "Téléphone": QLineEdit(),
            "Email": QLineEdit(),
            "Numéro de permis": QLineEdit(),
        }

        self.fields["Nom"].setPlaceholderText("Entrez le nom")
        self.fields["Post-Nom"].setPlaceholderText("Entrez le post-nom")
        self.fields["Prenom"].setPlaceholderText("Entrez le prénom")
        self.fields["Téléphone"].setPlaceholderText("Entrez  numéro de téléphone")
        self.fields["Email"].setPlaceholderText("exemple@email.com")
        self.fields["Numéro de permis"].setPlaceholderText("Numéro de permis")

        for i, (label, field) in enumerate(self.fields.items()):
            self.form_layout.addWidget(QLabel(f"{label.capitalize()}:"), i, 0)
            self.form_layout.addWidget(field, i, 1)

        # Groupe de boutons radio pour le sexe
        self.sex_group = QGroupBox()
        self.sex_layout = QHBoxLayout()
        self.radio_homme = QRadioButton("Homme")
        self.radio_femme = QRadioButton("Femme")
        self.radio_neutre = QRadioButton("Neutre")
        self.radio_homme.setChecked(True)

        self.sex_layout.addWidget(self.radio_homme)
        self.sex_layout.addWidget(self.radio_femme)
        self.sex_layout.addWidget(self.radio_neutre)
        self.sex_group.setLayout(self.sex_layout)

        self.form_layout.addWidget(QLabel("Sexe:"), len(self.fields), 0)
        self.form_layout.addWidget(self.sex_group, len(self.fields), 1)

        self.enregistrer_button = QPushButton("Enregistrer", clicked=self._enregistrer_chauffeur)
        self.form_layout.addWidget(self.enregistrer_button, len(self.fields) + 1, 0, 1, 2)

        self.form_group.setLayout(self.form_layout)
        self.main_layout.addWidget(self.form_group)

        # Liste des chauffeurs
        self.list_group = QGroupBox("Liste des Chauffeurs")
        self.list_layout = QVBoxLayout()
        self.search_input = QLineEdit()

        self.search_layout = QHBoxLayout()
        self.search_input.setPlaceholderText("Rechercher...")
        self.search_input.textChanged.connect(self._filter_chauffeur)
        self.search_layout.addWidget(self.search_input)
        self.list_layout.addLayout(self.search_layout)

        self.list_view = QListWidget()
        self.list_layout.addWidget(self.list_view)

        self.list_group.setLayout(self.list_layout)
        self.main_layout.addWidget(self.list_group)

        self.refresh_button = QPushButton("Actualiser la liste", clicked=self._load_chauffeurs)

        self.search_layout.addWidget(self.refresh_button)

        self._load_chauffeurs()

    def _show_message(self, title, message):
        QMessageBox.information(self, title, message)

    def _enregistrer_chauffeur(self):
        data = {key: field.text().strip() for key, field in self.fields.items()}
        if self.radio_homme.isChecked():
            data["sex"] = "Homme"
        elif self.radio_femme.isChecked():
            data["sex"] = "Femme"
        else:
            data["sex"] = "Neutre"

        if not all(data[key] for key in ["Nom", "Post-Nom", "Prenom", "Téléphone", "Numéro de permis"]) or not data["Téléphone"].isdigit():
            self._show_message("Erreur", "Les champs obligatoires doivent être remplis et le téléphone doit être numérique.")
            return

        if self.chauffeur_controller.new_driver(**data):
            self._show_message("Succès", "Chauffeur enregistré avec succès.")
            self._load_chauffeurs()
            self._clear_fields()

    def _clear_fields(self):
        for field_widget in self.fields.values():
            field_widget.clear()
        self.radio_homme.setChecked(True)

    def _load_chauffeurs(self):
        self.list_view.clear()
        try:
            for chauffeur in self.chauffeur_controller.get_all_drivers():
                widget_item = QWidget()
                item_layout = QHBoxLayout(widget_item)

                item_label = QLabel(
                    f"{chauffeur.nom} {chauffeur.postnom}, {chauffeur.prenom} - Tél: {chauffeur.telephone}, Permis: {chauffeur.numero_permis}, Sexe: {chauffeur.sex}"
                )

                btn_modifier = QPushButton("Modifier")
                btn_supprimer = QPushButton("Supprimer")

                btn_modifier.clicked.connect(partial(self._modify_chauffeur, chauffeur.id))
                btn_supprimer.clicked.connect(partial(self._delete_chauffeur, chauffeur.id))

                item_layout.addWidget(item_label)
                item_layout.addWidget(btn_modifier)
                item_layout.addWidget(btn_supprimer)
                item_layout.setContentsMargins(5, 5, 5, 5)

                widget_item.setLayout(item_layout)

                container = QListWidgetItem(self.list_view)
                container.setSizeHint(widget_item.sizeHint())
                self.list_view.addItem(container)
                self.list_view.setItemWidget(container, widget_item)

        except Exception as e:
            self._show_message("Erreur", f"Erreur de chargement : {str(e)}")

    def _filter_chauffeur(self):
        search_text = self.search_input.text().strip().lower()
        for i in range(self.list_view.count()):
            item_widget = self.list_view.itemWidget(self.list_view.item(i))
            if item_widget:
                item_label = item_widget.findChild(QLabel)
                if item_label:
                    self.list_view.item(i).setHidden(search_text not in item_label.text().lower())

    def _modify_chauffeur(self, chauffeur_id):
        try:
            if self.parent and hasattr(self.parent, "open_modify_chauffeur_page"):
                self.parent.open_modify_chauffeur_page(chauffeur_id)
            else:
                self._show_message("Erreur", "La fenêtre principale ne définit pas la méthode 'open_modify_chauffeur_page'.")
        except Exception as e:
            self._show_message("Erreur", f"Erreur lors de la modification : {str(e)}")

    def _delete_chauffeur(self, chauffeur_id):
        reply = QMessageBox.question(self, "Confirmation", "Voulez-vous vraiment supprimer ce chauffeur ?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                self.chauffeur_controller.delete_driver(chauffeur_id)
                self._show_message("Succès", "Chauffeur supprimé avec succès.")
                self._load_chauffeurs()
            except Exception as e:
                self._show_message("Erreur", f"Erreur lors de la suppression : {str(e)}")
