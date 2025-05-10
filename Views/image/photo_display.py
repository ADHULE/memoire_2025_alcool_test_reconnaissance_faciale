import logging
import os
import threading
import time
import cv2
import numpy as np
from PIL import Image
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from Controllers.chauffeur_controller import CHAUFFEUR_CONTROLLER
from Controllers.entrainement_controller import ENTRAINEMENT_CONTROLLER
from Controllers.image_controller import IMAGE_CONTROLLER

class DISPLAY_IMAGES(QWidget):
    """
    Widget pour afficher et gérer les images, avec fonctionnalités d'entraînement LBPH supprimées.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestion des Photos")
        self.parent = parent

        self.photo_controller = IMAGE_CONTROLLER()
        self.person_controller = CHAUFFEUR_CONTROLLER()
        self.all_photos = []

        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
        self.logger = logging.getLogger(__name__)

        self.setup_ui()
        QTimer.singleShot(0, self.load_images_from_controller)

    def setup_ui(self):
        """Configure l'interface utilisateur moderne et intuitive."""
        main_layout = QVBoxLayout()

        # Barre d'outils supérieure
        toolbar_layout = QHBoxLayout()

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Rechercher par nom")
        self.search_edit.textChanged.connect(self.filter_images)
        toolbar_layout.addWidget(self.search_edit)

        self.refresh_button = QPushButton("Actualiser")
        self.refresh_button.clicked.connect(self.load_images_from_controller)
        toolbar_layout.addWidget(self.refresh_button)

        main_layout.addLayout(toolbar_layout)

        # Zone d'affichage des images (Scrollable Grid)
        self.image_grid_widget = QWidget()
        self.image_grid_layout = QGridLayout()
        self.image_grid_widget.setLayout(self.image_grid_layout)

        self.image_scroll = QScrollArea()
        self.image_scroll.setWidgetResizable(True)
        self.image_scroll.setWidget(self.image_grid_widget)
        main_layout.addWidget(self.image_scroll)

        self.setLayout(main_layout)

    def load_images_from_controller(self):
        """Charge les images depuis le contrôleur et les affiche."""
        try:
            self.all_photos = self.photo_controller.get_all_photos()
            self._display_photos(self.all_photos)
        except Exception as e:
            self.logger.error(f"Erreur lors du chargement des images: {e}")
            self.show_message("Erreur", "Impossible de charger les images.")

    def _display_photos(self, photos):
        """Affiche les photos dans une grille."""
        self.clear_layout(self.image_grid_layout)
        columns = 4  # Nombre de colonnes fixes pour une meilleure organisation
        row, col = 0, 0
        for photo in photos:
            image_widget = self._create_photo_item(photo)
            self.image_grid_layout.addWidget(image_widget, row, col)
            col += 1
            if col >= columns:
                col = 0
                row += 1
        self.image_grid_widget.adjustSize()

    def _create_photo_item(self, photo):
        """Crée un widget pour afficher une photo individuelle."""
        item_widget = QWidget()
        item_layout = QVBoxLayout()
        item_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        pixmap = QPixmap(photo.url).scaled(200, 250, Qt.KeepAspectRatio)
        image_label = QLabel()
        image_label.setPixmap(pixmap)
        image_label.setAlignment(Qt.AlignCenter)
        item_layout.addWidget(image_label)

        person = self.person_controller.get_driver_by_id(photo.personne_id)
        name_label = QLabel(f"{person.nom} {person.prenom}" if person else "Inconnu")
        name_label.setAlignment(Qt.AlignCenter)
        item_layout.addWidget(name_label)

        buttons_layout = QHBoxLayout()
        modify_button = QPushButton("Modifier")
        modify_button.clicked.connect(lambda: self.modify_image(photo.id))
        buttons_layout.addWidget(modify_button)
        delete_button = QPushButton("Supprimer")
        delete_button.clicked.connect(lambda: self.delete_image(photo.id))
        buttons_layout.addWidget(delete_button)
        item_layout.addLayout(buttons_layout)

        item_widget.setLayout(item_layout)
        return item_widget

    def filter_images(self, text):
        """Filtre les images affichées en fonction du texte de recherche."""
        if not text:
            self._display_photos(self.all_photos)
            return
        filtered_photos = [
            p
            for p in self.all_photos
            if self.person_controller.get_driver_by_id(p.personne_id)
            and text.lower()
            in f"{self.person_controller.get_driver_by_id(p.personne_id).nom} {self.person_controller.get_driver_by_id(p.personne_id).prenom}".lower()
        ]
        self._display_photos(filtered_photos)

    def modify_image(self, photo_id):
        """Ouvre la page de modification pour l'image sélectionnée."""
        self.logger.debug(f"Modification de l'image ID: {photo_id}")
        if self.parent and hasattr(self.parent, 'open_modify_photo_page'):
            self.parent.open_modify_photo_page(photo_id)
        else:
            self.logger.error("self.parent invalide pour la modification.")
            self.show_message("Erreur", "Impossible d'ouvrir la page de modification.")

    def delete_image(self, photo_id):
        """Supprime l'image sélectionnée après confirmation."""
        confirmation = QMessageBox.question(
            self, "Confirmation", "Supprimer cette image ?", QMessageBox.Yes | QMessageBox.No
        )
        if confirmation == QMessageBox.Yes:
            try:
                if self.photo_controller.delete_photo(photo_id):
                    self.load_images_from_controller()
                    self.show_message("Succès", "Image supprimée.")
                else:
                    self.show_message("Erreur", "Échec de la suppression.")
            except Exception as e:
                self.logger.error(f"Erreur lors de la suppression de l'image: {e}")
                self.show_message("Erreur", "Erreur lors de la suppression.")

    def clear_layout(self, layout):
        """Efface tous les éléments d'un layout."""
        while layout.count():
            item = layout.takeAt(0)
            if widget := item.widget():
                widget.deleteLater()

    def show_message(self, title, message):
        """Affiche une boîte de message informative."""
        QMessageBox.information(self, title, message)

# Les fonctionnalités d'entraînement ont été supprimées de cette classe.