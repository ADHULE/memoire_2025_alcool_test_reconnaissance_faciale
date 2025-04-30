from PySide6.QtWidgets import *
from PySide6.QtCore import *
from Controllers.chauffeur_controller import CHAUFFEUR_CONTROLLER
from Controllers.image_controller import IMAGE_CONTROLLER

class IMAGE_VIEW(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestion des Photos")
        self.photo_controller, self.chauffeur_controller = IMAGE_CONTROLLER(), CHAUFFEUR_CONTROLLER()

        # **Layout principal**
        main_layout = QVBoxLayout(self)

        # **Formulaire Ajout d'Images**
        self.form_group = QGroupBox("Ajouter une image")
        self.form_layout = QGridLayout()

        self.url_input = self._create_line_edit("Sélectionner une image...")
        self.select_image_button = self._create_button("Parcourir...", self.browse_image)
        self.create_button = self._create_button("Créer", self.create_photo)

        self.form_layout.addWidget(QLabel("URL:"), 0, 0)
        self.form_layout.addWidget(self.url_input, 0, 1)
        self.form_layout.addWidget(self.select_image_button, 1, 0, 1, 2)
        self.form_layout.addWidget(self.create_button, 2, 0, 1, 2)

        self.form_group.setLayout(self.form_layout)
        main_layout.addWidget(self.form_group)

        # **Liste des Chauffeurs**
        self.list_group = QGroupBox("Associer une image à un chauffeur")
        self.list_layout = QVBoxLayout()

        self.filter_input = self._create_line_edit("Filtrer par nom", self.filter_chauffeurs)
        self.list_layout.addWidget(self.filter_input)

        self.chauffeur_list_layout, self.scroll_area = self._create_scrollable_area()
        self.list_layout.addWidget(self.scroll_area)

        self.chauffeur_radio_buttons = {}
        self.populate_chauffeur_list()

        self.list_group.setLayout(self.list_layout)
        main_layout.addWidget(self.list_group)

    def _create_line_edit(self, placeholder=None, callback=None):
        """Crée un champ de texte avec un placeholder et un callback facultatif."""
        line_edit = QLineEdit()
        if placeholder:
            line_edit.setPlaceholderText(placeholder)
        if callback:
            line_edit.textChanged.connect(callback)
        return line_edit

    def _create_button(self, text, callback):
        """Crée un bouton lié à une action."""
        button = QPushButton(text)
        button.clicked.connect(callback)
        return button

    def _create_scrollable_area(self):
        """Crée une zone de liste scrollable."""
        list_widget = QWidget()
        list_layout = QVBoxLayout()
        list_widget.setLayout(list_layout)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(list_widget)

        return list_layout, scroll_area

    def browse_image(self):
        """Ouvre une boîte de dialogue pour sélectionner une image."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Sélectionner une image", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        if file_path:
            self.url_input.setText(file_path)

    def populate_chauffeur_list(self, chauffeurs=None):
        """Ajoute les chauffeurs à la liste radio."""
        if chauffeurs is None:
            chauffeurs = self.chauffeur_controller.get_all_drivers()

        while self.chauffeur_list_layout.count():
            item = self.chauffeur_list_layout.takeAt(0)
            if widget := item.widget():
                widget.deleteLater()

        self.chauffeur_radio_buttons.clear()
        for chauffeur in chauffeurs:
            radio_button = QRadioButton(f"{chauffeur.nom} {chauffeur.prenom}")
            self.chauffeur_list_layout.addWidget(radio_button)
            self.chauffeur_radio_buttons[chauffeur.id] = radio_button

    def filter_chauffeurs(self, filter_text):
        """Filtre les chauffeurs selon le texte entré."""
        chauffeurs = self.chauffeur_controller.get_all_drivers()
        filtered_chauffeurs = [c for c in chauffeurs if filter_text.lower() in f"{c.nom} {c.prenom}".lower()]
        self.populate_chauffeur_list(filtered_chauffeurs)

    def create_photo(self):
        """Ajoute une image associée à un chauffeur."""
        file_path = self.url_input.text()
        personne_id = next((id for id, radio in self.chauffeur_radio_buttons.items() if radio.isChecked()), None)

        if file_path and personne_id:
            try:
                photo = self.photo_controller.add_photo(file_path, personne_id)
                msg = "Photo ajoutée avec succès." if photo else "Échec de l'ajout de la photo."
                QMessageBox.information(self, "Résultat", msg)
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Problème lors de l'ajout : {e}")
        else:
            QMessageBox.warning(self, "Avertissement", "Sélectionnez une image et un chauffeur.")
