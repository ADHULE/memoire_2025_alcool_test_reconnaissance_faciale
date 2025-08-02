from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel,
    QMessageBox, QDateEdit, QFormLayout, QScrollArea, QGridLayout, QFrame
)
from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QPixmap
from Controllers.historique_controller import HISTORIQUE_CONTROLLER
from Controllers.image_controller import IMAGE_CONTROLLER
import logging
from datetime import datetime
import os


class DISPLAY_HISTORY(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Historique des événements")

        self.history_controller = HISTORIQUE_CONTROLLER()
        self.image_controller = IMAGE_CONTROLLER()
        self.all_history = []

        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
        self.logger = logging.getLogger(__name__)

        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()

        # Barre de recherche
        toolbar_layout = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Rechercher par date/informations...")
        self.search_edit.textChanged.connect(self.filter_history)
        toolbar_layout.addWidget(self.search_edit)

        self.refresh_button = QPushButton("Actualiser")
        self.refresh_button.clicked.connect(self.load_history_from_controller)
        toolbar_layout.addWidget(self.refresh_button)

        main_layout.addLayout(toolbar_layout)

        # Filtres de date
        date_filter_layout = QFormLayout()
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(QDate.currentDate().addDays(-7))

        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDate(QDate.currentDate())



        # Scroll Area pour afficher les blocs
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.scroll_widget = QWidget()
        self.grid_layout = QGridLayout(self.scroll_widget)
        self.grid_layout.setAlignment(Qt.AlignTop)

        self.scroll_area.setWidget(self.scroll_widget)
        main_layout.addWidget(self.scroll_area)

        self.setLayout(main_layout)
        self.load_history_from_controller()

    def load_history_from_controller(self):
        try:
            self.all_history = self.history_controller.get_all_histories()
            self.display_history(self.all_history)
        except Exception as e:
            self.logger.error(f"Erreur lors du chargement de l'historique: {e}")
            self.show_message("Erreur", "Impossible de charger l'historique.")

    def display_history(self, histories):
        # Vider l'affichage précédent
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        for index, h in enumerate(histories):
            container = QFrame()
            container.setFrameShape(QFrame.StyledPanel)
            layout = QHBoxLayout(container)

            # Image
            image_label = QLabel()
            image_path = self.image_controller.get_image_path_by_id(h.image_id)
            if image_path and os.path.exists(image_path):
                pixmap = QPixmap(image_path).scaled(150, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                image_label.setPixmap(pixmap)
            else:
                image_label.setText("Image\nnon trouvée")
            image_label.setFixedSize(200, 100)
            image_label.setAlignment(Qt.AlignCenter)

            # Infos texte
            info_layout = QVBoxLayout()
            info_layout.addWidget(QLabel(f"<b>Date/Heure : </b> {h.jour_heure}"))
            info_layout.addWidget(QLabel(f"<b>Informations :</b>  {h.person_info}"))
            taux = f"{h.alcool_value:.2f}" if h.alcool_value is not None else "-"
            info_layout.addWidget(QLabel(f"<b>Taux d'alcool :</b>  {taux}"))
            # Bouton de suppression
            delete_btn = QPushButton("Supprimer")
            delete_btn.clicked.connect(lambda _, hid=h.id: self.delete_history(hid))
            info_layout.addWidget(delete_btn)

            layout.addWidget(image_label)
            layout.addLayout(info_layout)

            self.grid_layout.addWidget(container, index, 0)

    def delete_history(self, historique_id):
        confirmation = QMessageBox.question(
            self,
            "Confirmation de suppression",
            "Voulez-vous vraiment supprimer cet historique ?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirmation == QMessageBox.Yes:
            success = self.history_controller.delete_history(historique_id)
            if success:
                self.show_message("Succès", "Historique supprimé avec succès.")
                self.load_history_from_controller()
            else:
                self.show_message("Erreur", "Impossible de supprimer cet historique.")

    def filter_history(self, text):
        if not text:
            self.display_history(self.all_history)
            return
        filtered = [h for h in self.all_history if text.lower() in h.person_info.lower()]
        self.display_history(filtered)

    def filter_by_date(self):
        start_date = self.start_date_edit.date().toPython()
        end_date = self.end_date_edit.date().toPython()
        try:
            filtered = self.history_controller.get_by_date_range(start_date, end_date)
            self.display_history(filtered)
        except Exception as e:
            self.logger.error(f"Erreur de filtrage par date: {e}")
            self.show_message("Erreur", "Échec du filtrage par date.")

    def show_message(self, title, message):
        QMessageBox.information(self, title, message)
