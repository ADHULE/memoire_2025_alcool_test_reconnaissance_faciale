from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import QPixmap
from Controllers.image_controller import IMAGE_CONTROLLER
import logging

# Configuration de la journalisation
logging.basicConfig(level=logging.INFO)

class MODIFIER_IMAGES_PAGE(QDialog):
    def __init__(self, photo_id, parent=None):
        super(MODIFIER_IMAGES_PAGE, self).__init__(parent)
        self.setWindowTitle("Modifier Photo")
        self.resize(500, 350)

        # Identifiant de la photo à modifier et instanciation du contrôleur
        self.photo_id = photo_id
        self.photo_controller = IMAGE_CONTROLLER()

        # URL actuelle de la photo (sera chargée)
        self.current_photo_url = None

        # Configuration de la mise en page principale
        self.setLayout(self.create_main_layout())

        # Charger les données de la photo existante
        self._load_existing_photo_data()

        # Charger la feuille de style pour la personnalisation
        # self.load_stylesheet()

    def _load_existing_photo_data(self):
        """
        Charge les données de la photo existante et met à jour les champs.
        """
        try:
            photo_data = self.photo_controller.get_photo(self.photo_id)
            if photo_data and hasattr(photo_data, 'url'):
                self.current_photo_url = photo_data.url
                self.url_input.setText(self.current_photo_url)
                self._display_preview(self.current_photo_url)
                logging.info(f"Données de la photo chargées : {self.current_photo_url}")
            else:
                QMessageBox.warning(self, "Avertissement", "Impossible de charger les informations de la photo.")
                self.close()
        except Exception as e:
            logging.error(f"Erreur lors du chargement des données de la photo : {e}")
            QMessageBox.critical(self, "Erreur", "Une erreur s'est produite lors du chargement des données.")
            self.close()

    def create_main_layout(self):
        """
        Crée la mise en page principale.
        """
        self.hboxLayout = QHBoxLayout()
        self.hboxLayout.setSpacing(20)  # Espacement entre les colonnes

        # Partie gauche pour la sélection et l'aperçu de l'image
        self.leftLayout = QVBoxLayout()

        self.label_select_image = QLabel("Sélectionner une nouvelle image (facultatif)")
        self.leftLayout.addWidget(self.label_select_image)

        self.select_image_button = QPushButton("Parcourir...")
        self.select_image_button.clicked.connect(self.browse_image)
        self.leftLayout.addWidget(self.select_image_button)

        self.label_url = QLabel("URL")
        self.leftLayout.addWidget(self.label_url)
        self.url_input = QLineEdit()
        self.leftLayout.addWidget(self.url_input)

        self.image_preview = QLabel("Aperçu de l'image")
        self.image_preview.setFixedSize(200, 200)
        self.image_preview.setStyleSheet("border: 1px solid gray;")  # Ajouter une bordure
        self.image_preview.setAlignment(Qt.AlignCenter)
        self.leftLayout.addWidget(self.image_preview)

        self.modify_button = QPushButton("Enregistrer les modifications")
        self.modify_button.clicked.connect(self.modify_photo)
        self.leftLayout.addWidget(self.modify_button)

        self.hboxLayout.addLayout(self.leftLayout)
        return self.hboxLayout

    def browse_image(self):
        """
        Permet à l'utilisateur de sélectionner une image et de la prévisualiser.
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Sélectionner une image",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif)"  # Types d'images supportés
        )
        if file_path:
            self.url_input.setText(file_path)  # Affiche l'URL dans le champ de saisie
            self._display_preview(file_path)

    def _display_preview(self, image_path):
        """
        Affiche l'aperçu de l'image sélectionnée ou actuelle.
        """
        if image_path:
            pixmap = QPixmap(image_path)
            scaled_pixmap = pixmap.scaled(self.image_preview.width(), self.image_preview.height(), Qt.KeepAspectRatio)
            self.image_preview.setPixmap(scaled_pixmap)
            self.image_preview.setText("")  # Effacer le texte par défaut
        else:
            self.image_preview.clear()
            self.image_preview.setText("Aucun aperçu disponible")

    def modify_photo(self):
        """
        Met à jour la photo en fonction de l'URL et ferme la boîte de dialogue.
        """
        image_url = self.url_input.text()  # Récupère l'URL de l'image
        if not image_url:
            QMessageBox.warning(self, "Avertissement", "Veuillez fournir une URL d'image.")
            return

        try:
            # Mise à jour de la photo via le contrôleur
            updated_photo = self.photo_controller.update_photo(self.photo_id, new_url=image_url)
            if updated_photo:
                QMessageBox.information(self, "Succès", "Photo mise à jour avec succès !")
                logging.info(f"Photo mise à jour : {image_url}")
                self.accept()  # Ferme la boîte de dialogue avec un code d'acceptation
            else:
                QMessageBox.critical(self, "Erreur", "La mise à jour de la photo a échoué. Veuillez vérifier les données.")
        except Exception as e:
            logging.error(f"Erreur lors de la mise à jour de la photo : {e}")
            QMessageBox.critical(self, "Erreur", f"Une erreur s'est produite lors de la mise à jour : {e}")

    def load_stylesheet(self):
        """
        Charge une feuille de style pour personnaliser l'interface.
        """
        try:
            with open("Styles/dialog_style.css", "r") as file:
                self.setStyleSheet(file.read())
        except FileNotFoundError:
            QMessageBox.warning(self, "Avertissement", "La feuille de style est introuvable.")