import logging
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from Controllers.image_controller import IMAGE_CONTROLLER
from Controllers.chauffeur_controller import CHAUFFEUR_CONTROLLER

import os  # Gestion des fichiers et des répertoires
import cv2  # Bibliothèque OpenCV pour la vision par ordinateur (utilisée pour le traitement d'image)
import numpy as np  # Manipulation des tableaux numériques
from PIL import Image  # Bibliothèque pour manipuler les images
import threading  # Pour exécuter l'entraînement dans un thread séparé
import time

class DISPLAY_IMAGES(QWidget):
    # Déclaration des signaux pour l'entraînement.
    training_started_signal = Signal()
    training_progress_signal = Signal(int)
    training_completed_signal = Signal(bool, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Affichage et Entraînement des Photos")
        self.parent = parent  # Référence vers le parent

        # Initialisation des contrôleurs
        self.photo_controller = IMAGE_CONTROLLER()
        self.person_controller = CHAUFFEUR_CONTROLLER()

        # Création du modèle de reconnaissance faciale LBPH.
        # Pour sauvegarder sous YAML, il suffit d'utiliser l'extension appropriée lors de l'appel à .save().
        self.reconnaissance = cv2.face.LBPHFaceRecognizer_create()

        self.all_photos = []  # Stocke toutes les photos chargées

        # Configuration du logger
        logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
        self.logger = logging.getLogger(__name__)

        # Chemin par défaut pour le dossier de sauvegarde
        self.training_folder = ""

        # Label affichant le dossier de sauvegarde sélectionné
        self.save_folder_path_label = QLabel("Aucun dossier sélectionné")

        # Construction de l'interface utilisateur
        self.setLayout(self.setup_ui())

        # Connexion des signaux d'entraînement aux slots dédiés
        self.training_progress_signal.connect(self.update_training_progress)
        self.training_completed_signal.connect(self.training_completed)

        # Chargement non bloquant des images
        QTimer.singleShot(0, self.load_images_from_controller)

    def setup_ui(self):
        """Configure l'interface utilisateur principale."""
        main_layout = QHBoxLayout()

        # Bloc de gauche pour l'affichage des images
        left_widget = QWidget()
        left_layout = QVBoxLayout()

        # Barre de recherche
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Filtrer par nom, postnom ou prénom")
        self.search_edit.textChanged.connect(self.filter_images)
        left_layout.addWidget(self.search_edit)

        # Zone d'affichage des images
        self.image_grid_layout = QGridLayout()
        self.image_scroll = QScrollArea()
        self.image_scroll.setWidgetResizable(True)
        image_widget = QWidget()
        image_widget.setLayout(self.image_grid_layout)
        self.image_scroll.setWidget(image_widget)
        left_layout.addWidget(self.image_scroll)

        left_widget.setLayout(left_layout)

        # Bloc de droite pour l'entraînement
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("Entraînement des Photos"))

        self.refresh_train_list_button = QPushButton("Actualiser la liste")
        self.refresh_train_list_button.clicked.connect(self.load_images_from_controller)
        right_layout.addWidget(self.refresh_train_list_button)

        # Sélection du dossier de sauvegarde
        select_folder_layout = QHBoxLayout()
        self.select_folder_button = QPushButton("Sélectionner le dossier de sauvegarde")
        self.select_folder_button.clicked.connect(self.select_save_folder)
        select_folder_layout.addWidget(self.select_folder_button)
        select_folder_layout.addWidget(self.save_folder_path_label)
        right_layout.addLayout(select_folder_layout)

        self.training_progress_bar = QProgressBar()
        self.training_progress_bar.setVisible(False)
        right_layout.addWidget(self.training_progress_bar)

        self.start_training_button = QPushButton("Démarrer l'entraînement")
        self.start_training_button.clicked.connect(self.start_training)
        self.start_training_button.setEnabled(False)  # Désactivé initialement
        right_layout.addWidget(self.start_training_button)

        right_widget.setLayout(right_layout)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)

        main_layout.addWidget(splitter)
        return main_layout

    def load_images_from_controller(self):
        """Charger et afficher toutes les images depuis le contrôleur."""
        try:
            self.all_photos = self.photo_controller.get_all_photos()
            self.load_images(self.all_photos)
        except Exception as e:
            self.logger.exception("Erreur lors du chargement des images")
            self.show_message("Erreur", "Impossible de charger les images.")

    def load_images(self, photos):
        """Affiche les images avec gestion dynamique du nombre de colonnes."""
        self.clear_layout(self.image_grid_layout)
        container_width = self.image_scroll.width()
        image_width = 200
        columns = max(1, container_width // (image_width + 20))

        row, col = 0, 0
        for photo in photos:
            image_widget = self.create_image_widget(photo)
            self.image_grid_layout.addWidget(image_widget, row, col)
            col += 1
            if col >= columns:
                col = 0
                row += 1

        self.image_scroll.widget().adjustSize()

    def create_image_widget(self, photo):
        """Crée un widget individuel pour chaque image."""
        image_widget = QWidget()
        image_layout = QVBoxLayout()

        pixmap = QPixmap(photo.url).scaled(400, 500, Qt.KeepAspectRatio)
        image_label = QLabel()
        image_label.setPixmap(pixmap)
        image_label.setAlignment(Qt.AlignCenter)

        person = self.person_controller.get_driver(photo.personne_id)
        person_name = f"{person.nom} {person.postnom} {person.prenom}" if person else "Inconnu"

        name_label = QLabel(person_name)
        name_label.setAlignment(Qt.AlignCenter)

        modify_button = QPushButton("Modifier")
        modify_button.clicked.connect(lambda: self.modify_image(photo.id))

        delete_button = QPushButton("Supprimer")
        delete_button.clicked.connect(lambda: self.delete_image(photo.id))

        button_layout = QHBoxLayout()
        button_layout.addWidget(modify_button)
        button_layout.addWidget(delete_button)

        image_layout.addWidget(image_label)
        image_layout.addWidget(name_label)
        image_layout.addLayout(button_layout)

        image_widget.setLayout(image_layout)
        return image_widget

    def refresh_images(self):
        """Recharge toutes les images."""
        self.search_edit.clear()
        self.load_images(self.all_photos)

    def filter_images(self, text):
        """Filtrer les images en fonction du nom, postnom ou prénom."""
        if not text:
            self.load_images(self.all_photos)
            return

        filtered_photos = []
        for photo in self.all_photos:
            person = self.person_controller.get_driver(photo.personne_id)
            if person:
                full_name = f"{person.nom} {person.postnom} {person.prenom}".lower()
                if text.lower() in full_name:
                    filtered_photos.append(photo)
        self.load_images(filtered_photos)

    def modify_image(self, photo_id):
        """Ouvre une fenêtre pour modifier une image sélectionnée."""
        self.logger.debug(f"Tentative de modification de l'image avec ID: {photo_id}")
        if self.parent and hasattr(self.parent, 'open_modify_photo_page'):
            self.parent.open_modify_photo_page(photo_id)
        else:
            self.logger.error("Échec de la modification: self.parent est invalide")
            self.show_message("Erreur", "Impossible d'accéder à la modification de la photo.")

    def delete_image(self, photo_id):
        """Supprime une image après confirmation."""
        confirmation = QMessageBox.question(
            self, "Confirmation", "Voulez-vous vraiment supprimer cette image ?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirmation == QMessageBox.Yes:
            try:
                if self.photo_controller.delete_photo(photo_id):
                    # Recharge la liste complète des images après suppression.
                    self.load_images_from_controller()
                    self.show_message("Succès", "Image supprimée avec succès.")
                else:
                    self.show_message("Erreur", "Échec de la suppression.")
            except Exception as e:
                self.logger.exception("Erreur lors de la suppression d'une image")
                self.show_message("Erreur", "Erreur lors de la suppression de l'image.")

    def clear_layout(self, layout):
        """Supprime tous les widgets d'un layout."""
        while layout.count():
            item = layout.takeAt(0)
            if widget := item.widget():
                widget.deleteLater()

    def show_message(self, title, message):
        """Affiche un message d'information ou d'erreur."""
        QMessageBox.information(self, title, message)

    # ----- Fonctions d'entraînement et sauvegarde utilisant YAML -----

    def select_save_folder(self):
        """Permet à l'utilisateur de choisir un dossier de sauvegarde."""
        folder = QFileDialog.getExistingDirectory(None, "Sélectionner un dossier de sauvegarde", "")
        if folder:
            self.training_folder = folder
            self.save_folder_path_label.setText(f"Dossier sélectionné : {self.training_folder}")
            self.start_training_button.setEnabled(True)
        else:
            QMessageBox.warning(None, "Avertissement", "Aucun dossier sélectionné!")
            self.training_folder = ""
            self.save_folder_path_label.setText("Aucun dossier sélectionné")
            self.start_training_button.setEnabled(False)

    def get_training_data(self):
        """
        Récupère les images et leurs identifiants pour l'entraînement.
        Chaque image est chargée, convertie en niveaux de gris et redimensionnée en 200x200 pixels
        afin d'obtenir une entrée uniforme pour le modèle.
        """
        photos = self.photo_controller.get_all_photos()
        if not photos:
            raise ValueError("Aucune photo disponible pour l'entraînement.")

        faces, ids = [], []
        for photo in photos:
            image_path, person_id = photo.url, photo.personne_id
            if os.path.exists(image_path):
                try:
                    image = Image.open(image_path).convert("L")
                    image = image.resize((200, 200))
                    face_np = np.array(image, np.uint8)
                    faces.append(face_np)
                    ids.append(person_id)
                except Exception as e:
                    self.logger.error(f"Erreur lors du traitement de l'image {image_path}: {e}")
            else:
                self.logger.warning(f"Fichier introuvable: {image_path}")
        return np.array(ids), faces

    def train_model(self):
        """
        Méthode exécutée dans un thread qui effectue la montée en charge de la barre de progression
        en deux phases :
          - Phase 1 (0-50%) : Prétraitement des images.
          - Phase 2 (50-90%) : Entraînement effectif du modèle.
        À la fin, le modèle est sauvegardé au format YAML grâce à la méthode `save` de lbph.
        """
        try:
            ids, faces = self.get_training_data()
            num_images = len(faces)
            if num_images == 0:
                self.training_completed_signal.emit(False, "Aucune image détectée pour l'entraînement.")
                return

            self.training_started_signal.emit()

            # Phase 1 : Prétraitement (progression 0 à 50%)
            for i in range(num_images):
                time.sleep(0.1)  # Simulation d'un délai de traitement
                progress = int((i + 1) / num_images * 50)
                self.training_progress_signal.emit(progress)

            # Entraînement effectif du modèle
            self.reconnaissance.train(faces, ids)

            # Phase 2 : Simulation de progression pendant l'entraînement (50 à 90%)
            for step in range(1, 11):
                time.sleep(0.1)
                progress = 50 + int(step * 4)  # Progression de 54 à 90%
                self.training_progress_signal.emit(progress)

            # Sauvegarde du modèle au format YAML
            save_path = os.path.join(self.training_folder, "trainingdata.yml")
            self.reconnaissance.save(save_path)
            self.training_completed_signal.emit(True, f"Modèle entraîné et sauvegardé dans {save_path}")

        except Exception as e:
            self.logger.exception("Erreur lors de l'entraînement du modèle")
            self.training_completed_signal.emit(False, f"Erreur lors de l'entraînement: {e}")
        finally:
            self.training_progress_signal.emit(100)

    def start_training(self):
        """Démarre l'entraînement dans un thread séparé."""
        if not self.training_folder:
            QMessageBox.warning(None, "Avertissement", "Sélectionnez un dossier de sauvegarde avant l'entraînement!")
            return

        self.training_progress_bar.setValue(0)
        self.training_progress_bar.setVisible(True)
        self.start_training_button.setEnabled(False)

        self.training_thread = threading.Thread(target=self.train_model)
        self.training_thread.start()

    @Slot(int)
    def update_training_progress(self, progress):
        """Met à jour la barre de progression pendant l'entraînement."""
        self.training_progress_bar.setValue(progress)

    @Slot(bool, str)
    def training_completed(self, success, message):
        """Méthode appelée à la fin de l'entraînement."""
        self.training_progress_bar.setVisible(False)
        self.start_training_button.setEnabled(True)
        self.show_message("Entraînement", message)