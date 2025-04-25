from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from Controllers.etudiant_controller import EtudiantController
from Controllers.photo_controller import Photocontroller


class PhotoView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Photos")
        self.photo_controller = Photocontroller()
        self.etudiant_controller = EtudiantController()

        # Initialisation des layouts principaux
        self.hboxLayout = QHBoxLayout()
        self.hboxLayout.setSpacing(20)  # Espacement entre les colonnes

        # Partie gauche (ajout de l'image)
        self.leftLayout = self.create_left_layout()

        # Partie droite (liste des étudiants)
        self.rightLayout = self.create_right_layout()

        # Ajouter les layouts à l'hboxLayout
        self.hboxLayout.addWidget(self.create_frame(self.leftLayout))
        self.hboxLayout.addWidget(self.create_frame(self.rightLayout))
        self.setLayout(self.hboxLayout)

    def create_left_layout(self):
        """Créer le layout de la partie gauche pour l'ajout de l'image."""
        leftLayout = QVBoxLayout()

        # Titre
        title_label = self.create_label("AJOUTER L'IMAGE", object_name="titleLabel")
        leftLayout.addWidget(title_label)

        # Sélection de l'image
        self.label_select_image = self.create_label("Sélectionner une image")
        self.select_image_button = self.create_button("Parcourir...", self.browse_image)
        leftLayout.addWidget(self.label_select_image)
        leftLayout.addWidget(self.select_image_button)

        # Champ pour l'URL
        self.label_url = self.create_label("URL")
        self.url_input = self.create_line_edit()
        leftLayout.addWidget(self.label_url)
        leftLayout.addWidget(self.url_input)

        # Bouton de création
        self.create_button = self.create_button("Créer", self.create_photo)
        leftLayout.addWidget(self.create_button)

        return leftLayout

    def create_right_layout(self):
        """Créer le layout de la partie droite pour la liste des étudiants."""
        rightLayout = QVBoxLayout()

        # Barre de filtre
        self.filter_input = self.create_line_edit("Filtrer par nom")
        self.filter_input.textChanged.connect(self.filter_etudiants)
        rightLayout.addWidget(self.filter_input)

        # Liste des étudiants
        self.etudiant_list_layout, self.scroll_area = self.create_scrollable_area()
        
        rightLayout.addWidget(self.scroll_area)

        # Réinitialiser les données
        self.etudiant_radio_buttons = {}
        self.populate_etudiant_list()

        return rightLayout

    def create_scrollable_area(self):
        """Créer un layout avec zone défilante pour les étudiants."""
        list_widget = QWidget()
        list_layout = QVBoxLayout()
        list_layout.setAlignment(Qt.AlignTop)
        list_widget.setLayout(list_layout)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(list_widget)

        return list_layout, scroll_area

    def create_label(self, text, object_name=None):
        """Créer un label avec texte et optionnellement un nom d'objet."""
        label = QLabel(text)
        if object_name:
            label.setObjectName(object_name)
        return label

    def create_line_edit(self, placeholder=None):
        """Créer un champ de saisie avec un placeholder."""
        line_edit = QLineEdit()
        if placeholder:
            line_edit.setPlaceholderText(placeholder)
        return line_edit

    def create_button(self, text, callback):
        """Créer un bouton avec texte et fonction de rappel."""
        button = QPushButton(text)
        button.clicked.connect(callback)
        return button

    def browse_image(self):
        """Sélectionner une image et mettre à jour l'URL dans le champ de texte."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Sélectionner une image",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif)",
        )
        if file_path:
            self.url_input.setText(file_path)

    def populate_etudiant_list(self, etudiants=None):
        """Afficher les étudiants dans une liste déroulante."""
        if etudiants is None:
            etudiants = self.etudiant_controller.get_etudiants()

        # Réinitialiser les boutons radio
        while self.etudiant_list_layout.count():
            item = self.etudiant_list_layout.takeAt(0)
            if widget := item.widget():
                widget.deleteLater()

        self.etudiant_radio_buttons.clear()

        for etudiant in etudiants:
            radio_button = QRadioButton(f"{etudiant.nom} {etudiant.prenom}")
            self.etudiant_list_layout.addWidget(radio_button)
            self.etudiant_radio_buttons[etudiant.id] = radio_button

    def filter_etudiants(self, filter_text):
        """Filtrer les étudiants selon le texte saisi."""
        etudiants = self.etudiant_controller.get_etudiants()
        filtered_etudiants = [
            etudiant
            for etudiant in etudiants
            if filter_text.lower() in f"{etudiant.nom} {etudiant.prenom}".lower()
        ]
        self.populate_etudiant_list(filtered_etudiants)

    def create_photo(self):
        """Créer une photo et l'associer à un étudiant sélectionné."""
        file_path = self.url_input.text()
        personne_id = next(
            (
                etudiant_id
                for etudiant_id, radio_button in self.etudiant_radio_buttons.items()
                if radio_button.isChecked()
            ),
            None,
        )

        if file_path and personne_id:
            try:
                photo = self.photo_controller.add_photo(file_path, personne_id)
                if photo:
                    QMessageBox.information(
                        self, "Succès", "Photo ajoutée avec succès."
                    )
                else:
                    QMessageBox.warning(
                        self, "Avertissement", "Échec de l'ajout de la photo."
                    )
            except Exception as e:
                QMessageBox.critical(
                    self, "Erreur", f"Erreur lors de l'ajout de la photo : {e}"
                )
        else:
            QMessageBox.warning(
                self, "Avertissement", "Veuillez sélectionner une image et un étudiant."
            )

    def create_frame(self, layout):

        frame = QFrame()
        frame.setObjectName("forme_frame")
        frame.setLayout(layout)

        # Style de bordure et apparence générale
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setFrameShadow(QFrame.Raised)
        frame.setLineWidth(1)
        return frame
