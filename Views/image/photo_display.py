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
    training_started_signal = Signal()
    training_progress_signal = Signal(int)
    training_completed_signal = Signal(bool, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestion et Entraînement des Photos")
        self.parent = parent

        self.photo_controller = IMAGE_CONTROLLER()
        self.person_controller = CHAUFFEUR_CONTROLLER()
        self.entrainement_controller = ENTRAINEMENT_CONTROLLER()
        self.reconnaissance = cv2.face.LBPHFaceRecognizer_create()
        self.all_photos = []
        self.save_folder = None  # Variable pour stocker le dossier de sauvegarde sélectionné
        self.model_file_path = None # Variable pour stocker le chemin du fichier de modèle

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

        # Barre d'entraînement en bas
        training_bar_layout = QHBoxLayout()
        training_bar_layout.addWidget(QLabel("Entraînement:"))

        self.training_progress_bar = QProgressBar()
        self.training_progress_bar.setVisible(False)
        training_bar_layout.addWidget(self.training_progress_bar)

        # Label pour afficher le dossier de sauvegarde sélectionné
        self.selected_folder_label = QLabel("Aucun dossier sélectionné")
        training_bar_layout.addWidget(self.selected_folder_label)

        self.select_folder_button = QPushButton("Sélectionner le dossier de sauvegarde")
        self.select_folder_button.clicked.connect(self._select_save_folder) # Utilisation d'une nouvelle méthode interne
        training_bar_layout.addWidget(self.select_folder_button)

        self.start_training_button = QPushButton("Démarrer l'entraînement")
        self.start_training_button.clicked.connect(self.start_training)
        self.start_training_button.setEnabled(False)  # Désactivé initialement
        training_bar_layout.addWidget(self.start_training_button)

        main_layout.addLayout(training_bar_layout)

        self.setLayout(main_layout)

        self.training_progress_signal.connect(self.update_training_progress)
        self.training_completed_signal.connect(self.training_completed)

    def _select_save_folder(self):
        """Méthode interne pour gérer la sélection du dossier de sauvegarde."""
        folder = QFileDialog.getExistingDirectory(self, "Sélectionner le dossier de sauvegarde")
        if folder:
            self.save_folder = folder
            self.model_file_path = os.path.join(self.save_folder, "training_data.yml") # Définit le chemin du fichier de modèle
            self.selected_folder_label.setText(f"Dossier sélectionné: {self.save_folder}") # Rendre le dossier visible
            self.logger.info(f"Dossier de sauvegarde sélectionné : {self.save_folder}")
            self.start_training_button.setEnabled(True)  # Activer le bouton une fois le dossier sélectionné
        else:
            self.logger.info("Sélection du dossier de sauvegarde annulée.")
            self.selected_folder_label.setText("Aucun dossier sélectionné") # Mettre à jour le label
            self.start_training_button.setEnabled(False)

    def load_images_from_controller(self):
        try:
            self.all_photos = self.photo_controller.get_all_photos()
            self._display_photos(self.all_photos)
        except Exception as e:
            self.logger.error(f"Erreur lors du chargement des images: {e}")
            self.show_message("Erreur", "Impossible de charger les images.")

    def _display_photos(self, photos):
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
        self.logger.debug(f"Modification de l'image ID: {photo_id}")
        if self.parent and hasattr(self.parent, 'open_modify_photo_page'):
            self.parent.open_modify_photo_page(photo_id)
        else:
            self.logger.error("self.parent invalide pour la modification.")
            self.show_message("Erreur", "Impossible d'ouvrir la page de modification.")

    def delete_image(self, photo_id):
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
        while layout.count():
            item = layout.takeAt(0)
            if widget := item.widget():
                widget.deleteLater()

    def show_message(self, title, message):
        QMessageBox.information(self, title, message)

    def get_training_data(self):
        faces = []
        ids = []
        for photo in self.all_photos:
            try:
                img = cv2.imread(photo.url)
                if img is not None:
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    faces.append(gray)
                    ids.append(photo.personne_id)
                else:
                    self.logger.warning(f"Impossible de lire l'image pour l'entraînement: {photo.url}")
            except Exception as e:
                self.logger.error(f"Erreur de traitement de l'image pour l'entraînement {photo.url}: {e}")
        return np.array(ids), faces

    def start_training(self):
        if not self.save_folder:
            self.show_message("Avertissement", "Veuillez sélectionner un dossier de sauvegarde avant de démarrer l'entraînement.")
            return

        if os.path.exists(self.model_file_path):
            reply = QMessageBox.question(
                self,
                "Confirmation",
                "Un fichier d'entraînement existant a été trouvé. Voulez-vous le mettre à jour ?\nSi non, veuillez sélectionner un autre dossier.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                self._select_save_folder() # Permettre à l'utilisateur de sélectionner un autre dossier
                return

        self.training_progress_bar.setValue(0)
        self.training_progress_bar.setVisible(True)
        self.start_training_button.setEnabled(False)
        threading.Thread(target=self._train_model).start()

    def _train_model(self):
        try:
            ids, faces = self.get_training_data()
            if not faces:
                self.training_completed_signal.emit(False, "Aucune image de visage trouvée pour l'entraînement.")
                return

            self.training_started_signal.emit()
            num_faces = len(faces)
            for i, face in enumerate(faces):
                if face is not None and face.size > 0:
                    pass  # L'entraînement se fait sur toutes les faces en une seule fois
                progress = int((i + 1) / num_faces * 50)
                self.training_progress_signal.emit(progress)

            # Tentative de chargement du modèle existant
            if os.path.exists(self.model_file_path):
                try:
                    self.reconnaissance.read(self.model_file_path)
                    self.logger.info(f"Modèle existant chargé depuis : {self.model_file_path}")
                    # Entraîner le modèle existant avec les nouvelles données
                    self.reconnaissance.update(faces, np.array(ids))
                    self.logger.info("Modèle existant mis à jour avec de nouvelles images.")
                except Exception as e:
                    self.logger.error(f"Erreur lors du chargement du modèle existant : {e}")
                    self.reconnaissance.train(faces, np.array(ids))
                    self.logger.info("Aucun modèle existant valide trouvé, un nouveau modèle a été entraîné.")
            else:
                # Si aucun modèle existant, entraîner un nouveau
                self.reconnaissance.train(faces, np.array(ids))
                self.logger.info("Nouveau modèle entraîné.")

            for step in range(1, 51):
                time.sleep(0.02)
                self.training_progress_signal.emit(50 + step)

            if self.save_folder:
                try:
                    self.reconnaissance.save(self.model_file_path)
                    self.training_completed_signal.emit(True, f"Modèle entraîné et sauvegardé dans : {self.model_file_path}")
                    self.logger.info(f"Modèle entraîné et sauvegardé dans : {self.model_file_path}")
                except Exception as e:
                    error_message = f"Erreur lors de la sauvegarde du modèle dans le dossier sélectionné : {e}"
                    self.logger.error(error_message)
                    self.training_completed_signal.emit(False, error_message)
            else:
                self.training_completed_signal.emit(False, "Aucun dossier de sauvegarde sélectionné.")

        except Exception as e:
            self.logger.error(f"Erreur lors de l'entraînement du modèle: {e}")
            self.training_completed_signal.emit(False, f"Erreur d'entraînement: {e}")
        finally:
            self.training_progress_signal.emit(100)
            QMetaObject.invokeMethod(self, "reset_training_ui", Qt.QueuedConnection)

    @Slot(int)
    def update_training_progress(self, progress):
        self.training_progress_bar.setValue(progress)

    @Slot(bool, str)
    def training_completed(self, success, message):
        self.training_progress_bar.setVisible(False)
        self.start_training_button.setEnabled(True)
        self.show_message("Entraînement", message)
        if success:
            self.logger.info("Entraînement réussi.")
        else:
            self.logger.error(f"Échec de l'entraînement: {message}")

    @Slot()
    def reset_training_ui(self):
        self.training_progress_bar.setVisible(False)
        self.training_progress_bar.setValue(0)
        self.start_training_button.setEnabled(self.save_folder is not None)

