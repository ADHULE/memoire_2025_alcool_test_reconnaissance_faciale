from PySide6.QtWidgets import *
from PySide6.QtCore import *
from Controllers.chauffeur_controller import CHAUFFEUR_CONTROLLER
from Controllers.image_controller import IMAGE_CONTROLLER
from Views.image.camera_view import CameraView # Importez la nouvelle vue caméra

class IMAGE_VIEW(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestion des Photos")
        self.photo_controller, self.chauffeur_controller = IMAGE_CONTROLLER(), CHAUFFEUR_CONTROLLER()
        self.selected_chauffeur_id = None
        self.camera_view = None # Instance de la vue caméra

        # Layout principal
        main_layout = QVBoxLayout(self)

        # Sélection du Chauffeur (avant l'ajout)
        self.chauffeur_group = QGroupBox("Sélectionner un chauffeur pour la photo")
        
        self.chauffeur_layout = QVBoxLayout()

        self.filter_chauffeur_input = self._create_line_edit("Filtrer par nom", self.filter_chauffeurs)
        self.chauffeur_layout.addWidget(self.filter_chauffeur_input)
        actualiser_buton=self._create_button("actualiser",self.filter_chauffeurs)
        self.chauffeur_layout.addWidget(actualiser_buton)
        self.chauffeur_list_layout, self.chauffeur_scroll_area = self._create_scrollable_area()
        self.chauffeur_layout.addWidget(self.chauffeur_scroll_area)

        self.chauffeur_radio_buttons = {}
        self.populate_chauffeur_list()
        self.chauffeur_group.setLayout(self.chauffeur_layout)
        main_layout.addWidget(self.chauffeur_group)

        # Bouton pour ouvrir la caméra
        self.open_camera_button = self._create_button("Ouvrir la caméra", self.open_camera_page)
        main_layout.addWidget(self.open_camera_button)

        # Formulaire Ajout d'Images (pour parcourir les fichiers)
        self.form_group = QGroupBox("Ajouter une image depuis un fichier")
        self.form_layout = QGridLayout()

        self.url_input = self._create_line_edit("Sélectionner une image...")
        self.select_image_button = self._create_button("Parcourir...", self.browse_image)
        self.add_existing_button = self._create_button("Ajouter l'image sélectionnée", self.add_existing_photo)
        self.add_existing_button.setEnabled(False) # Désactivé au début

        self.form_layout.addWidget(QLabel("URL:"), 0, 0)
        self.form_layout.addWidget(self.url_input, 0, 1)
        self.form_layout.addWidget(self.select_image_button, 1, 0, 1, 2)
        self.form_layout.addWidget(self.add_existing_button, 2, 0, 1, 2)

        self.form_group.setLayout(self.form_layout)
        main_layout.addWidget(self.form_group)

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

    def populate_chauffeur_list(self, chauffeurs=None):
        """Ajoute les chauffeurs à la liste radio et permet la sélection."""
        if chauffeurs is None:
            chauffeurs = self.chauffeur_controller.get_all_drivers()

        while self.chauffeur_list_layout.count():
            item = self.chauffeur_list_layout.takeAt(0)
            if widget := item.widget():
                widget.deleteLater()

        self.chauffeur_radio_buttons.clear()
        for chauffeur in chauffeurs:
            radio_button = QRadioButton(f"{chauffeur.nom} {chauffeur.prenom}")
            radio_button.toggled.connect(lambda checked, id=chauffeur.id: self.chauffeur_selected(id, checked))
            self.chauffeur_list_layout.addWidget(radio_button)
            self.chauffeur_radio_buttons[chauffeur.id] = radio_button

        # Sélectionner le premier chauffeur par défaut s'il y en a
        if self.chauffeur_radio_buttons:
            first_id = list(self.chauffeur_radio_buttons.keys())[0]
            self.chauffeur_radio_buttons[first_id].setChecked(True)
            self.selected_chauffeur_id = first_id
            if hasattr(self, 'open_camera_button'): # Vérifiez si l'attribut existe
                self.open_camera_button.setEnabled(True)
            if hasattr(self, 'select_image_button'): # Vérifiez si l'attribut existe
                self.select_image_button.setEnabled(True)
        else:
            self.selected_chauffeur_id = None
            QMessageBox.warning(self, "Avertissement", "Aucun chauffeur trouvé. Veuillez en ajouter.")
            if hasattr(self, 'open_camera_button'):
                self.open_camera_button.setEnabled(False)
            if hasattr(self, 'select_image_button'):
                self.select_image_button.setEnabled(False)

    def chauffeur_selected(self, chauffeur_id, checked):
        """Mémorise l'ID du chauffeur sélectionné."""
        if checked:
            self.selected_chauffeur_id = chauffeur_id
            if hasattr(self, 'open_camera_button'):
                self.open_camera_button.setEnabled(True)
            if hasattr(self, 'select_image_button'):
                self.select_image_button.setEnabled(True)

    def filter_chauffeurs(self, filter_text):
        """Filtre les chauffeurs selon le texte entré."""
        chauffeurs = self.chauffeur_controller.get_all_drivers()
        filtered_chauffeurs = [c for c in chauffeurs if filter_text.lower() in f"{c.nom} {c.prenom}".lower()]
        self.populate_chauffeur_list(filtered_chauffeurs)

    def open_camera_page(self):
        """Ouvre la page dédiée à la caméra."""
        if self.selected_chauffeur_id is not None:
            self.camera_view = CameraView()
            # Vous pourriez passer l'ID du chauffeur à la CameraView si nécessaire
            self.camera_view.set_chauffeur_id(self.selected_chauffeur_id)
            self.camera_view.show()
            # Connecter un signal de la CameraView pour récupérer le chemin de l'image enregistrée
            self.camera_view.finished.connect(self.handle_captured_image_path) # Assurez-vous que 'finished' est émis
        else:
            QMessageBox.warning(self, "Avertissement", "Veuillez sélectionner un chauffeur avant d'ouvrir la caméra.")

    def handle_captured_image_path(self, file_path):
        """Récupère le chemin de l'image capturée depuis la CameraView."""
        if file_path:
            self.add_photo_to_database(file_path)

    def browse_image(self):
        """Ouvre une boîte de dialogue pour sélectionner une image existante."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Sélectionner une image", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        if file_path:
            self.url_input.setText(file_path)
            self.add_existing_button.setEnabled(True) # Activer le bouton d'ajout

    def add_existing_photo(self):
        """Ajoute une image existante associée au chauffeur sélectionné."""
        file_path = self.url_input.text()
        if file_path and self.selected_chauffeur_id:
            self.add_photo_to_database(file_path)
        else:
            QMessageBox.warning(self, "Avertissement", "Veuillez sélectionner un chauffeur et une image.")

    def add_photo_to_database(self, file_path):
        """Ajoute l'URL de la photo à la base de données pour le chauffeur sélectionné."""
        try:
            photo = self.photo_controller.add_photo(file_path, self.selected_chauffeur_id)
            msg = "Photo ajoutée avec succès." if photo else "Échec de l'ajout de la photo."
            QMessageBox.information(self, "Résultat", msg)
            self.url_input.clear()
            self.add_existing_button.setEnabled(False)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Problème lors de l'ajout : {e}")