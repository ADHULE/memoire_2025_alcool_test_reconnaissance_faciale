from PySide6.QtWidgets import *
from PySide6.QtCore import *
from Controllers.chauffeur_controller import CHAUFFEUR_CONTROLLER

class ENREGISTREMENT_CHAUFFEUR(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestion des Chauffeurs")
        self.parent = parent  # Référence à la fenêtre principale
        self.chauffeur_controller = CHAUFFEUR_CONTROLLER()

        # Layout principal
        self.main_layout = QVBoxLayout(self)

        # Formulaire d'enregistrement
        self.form_group = QGroupBox("Informations du Chauffeur")
        self.form_layout = QGridLayout()

        self.fields = {
            "nom": QLineEdit(),
            "postnom": QLineEdit(),
            "prenom": QLineEdit(),
            "telephone": QLineEdit(),
            "email": QLineEdit(),
            "numero_permis": QLineEdit(),
        }

        for i, (label, field) in enumerate(self.fields.items()):
            self.form_layout.addWidget(QLabel(f"{label.capitalize()}:"), i, 0)
            self.form_layout.addWidget(field, i, 1)

        self.enregistrer_button = QPushButton("Enregistrer", clicked=self._enregistrer_chauffeur)
        self.form_layout.addWidget(self.enregistrer_button, len(self.fields), 0, 1, 2)

        self.form_group.setLayout(self.form_layout)
        self.main_layout.addWidget(self.form_group)

        # Zone de recherche et liste des chauffeurs
        self.list_group = QGroupBox("Liste des Chauffeurs")
        self.list_layout = QVBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher...")
        self.search_input.textChanged.connect(self._filter_chauffeur)
        self.list_layout.addWidget(self.search_input)

        self.list_view = QListWidget()
        self.list_layout.addWidget(self.list_view)

        self.list_group.setLayout(self.list_layout)
        self.main_layout.addWidget(self.list_group)

        self.refresh_button = QPushButton("Rafraîchir", clicked=self._load_chauffeurs)
        self.main_layout.addWidget(self.refresh_button)

        self._load_chauffeurs()

    def _show_message(self, title, message):
        QMessageBox.information(self, title, message)

    def _enregistrer_chauffeur(self):
        """Enregistre un chauffeur après validation."""
        data = {key: field.text().strip() for key, field in self.fields.items()}
        if not all(data.values()) or not data["telephone"].isdigit():
            self._show_message("Erreur", "Tous les champs doivent être remplis correctement.")
            return

        if self.chauffeur_controller.new_driver(**data):
            self._show_message("Succès", "Chauffeur enregistré avec succès.")
            self._load_chauffeurs()
            self._clear_fields()
            
    def _clear_fields(self):
        for field in self.fields:
            field.itemAt(1).widget().clear()

       
    def _load_chauffeurs(self):
        """Charge et affiche la liste des chauffeurs avec les boutons Modifier et Supprimer."""
        self.list_view.clear()
        try:
            for chauffeur in self.chauffeur_controller.get_all_drivers():
                widget_item = QWidget()
                item_layout = QHBoxLayout(widget_item)

                item_label = QLabel(f"{chauffeur.nom} {chauffeur.postnom}, {chauffeur.prenom} - Tél: {chauffeur.telephone}, Permis: {chauffeur.numero_permis}")

                btn_modifier = QPushButton("Modifier")
                btn_supprimer = QPushButton("Supprimer")

                btn_modifier.clicked.connect(lambda _, id=chauffeur.id: self._modify_chauffeur(id))
                btn_supprimer.clicked.connect(lambda _, id=chauffeur.id: self._delete_chauffeur(id))

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
        """Filtre la liste des chauffeurs."""
        search_text = self.search_input.text().strip().lower()
        for i in range(self.list_view.count()):
            item_widget = self.list_view.itemWidget(self.list_view.item(i))
            if item_widget:
                item_label = item_widget.findChild(QLabel)
                item_widget.setVisible(search_text in item_label.text().lower())

    def _modify_chauffeur(self, chauffeur_id):
        """Ouvre la fenêtre de modification du chauffeur."""
        try:
            if self.parent and hasattr(self.parent, "open_modify_chauffeur_page"):
                self.parent.open_modify_chauffeur_page(chauffeur_id)
            else:
                raise AttributeError("La fenêtre principale ne définit pas la méthode de modification.")
        except Exception as e:
            self._show_message("Erreur", f"Erreur lors de la modification du chauffeur : {str(e)}")

    def _delete_chauffeur(self, chauffeur_id):
        """Supprime un chauffeur avec confirmation."""
        reply = QMessageBox.question(self, "Confirmation", "Voulez-vous vraiment supprimer ce chauffeur ?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                self.chauffeur_controller.delete_driver(chauffeur_id)
                self._show_message("Succès", "Chauffeur supprimé avec succès.")
                self._load_chauffeurs()
            except Exception as e:
                self._show_message("Erreur", f"Erreur lors de la suppression : {str(e)}")
