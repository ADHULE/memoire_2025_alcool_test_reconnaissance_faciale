from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit,
    QMessageBox, QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
    QDateEdit, QFormLayout
)
from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QPixmap
from Controllers.historique_controller import HISTORIQUE_CONTROLLER
import logging
from datetime import datetime
import os


class DISPLAY_HISTORY(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Historique des événements")
        self.resize(1100, 600)

        self.history_controller = HISTORIQUE_CONTROLLER()
        self.all_history = []

        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
        self.logger = logging.getLogger(__name__)

        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()

        # Barre de recherche et bouton actualiser
        toolbar_layout = QHBoxLayout()

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Rechercher par type d'événement (person_info)")
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

        self.date_filter_button = QPushButton("Filtrer par date")
        self.date_filter_button.clicked.connect(self.filter_by_date)


        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Date/Heure", "Événement", "Taux Alcool", "Image", "Action"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        main_layout.addWidget(self.table)

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
        self.table.setRowCount(0)
        for row, h in enumerate(histories):
            self.table.insertRow(row)

            # Colonne 0 : Date/heure
            self.table.setItem(row, 0, QTableWidgetItem(str(h.jour_heure)))

            # Colonne 1 : Person Info
            self.table.setItem(row, 1, QTableWidgetItem(h.person_info))

            # Colonne 2 : Taux d'alcool
            alcool_display = f"{h.alcool_value:.2f}" if h.alcool_value is not None else "-"
            self.table.setItem(row, 2, QTableWidgetItem(alcool_display))

            # Colonne 3 : Image
            image_label = QLabel()
            image_path = self.get_image_path(h.image_id)

            if image_path and os.path.exists(image_path):
                pixmap = QPixmap(image_path).scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                image_label.setPixmap(pixmap)
            else:
                image_label.setText("Image non trouvée")

            image_label.setAlignment(Qt.AlignCenter)
            self.table.setCellWidget(row, 3, image_label)

            # Colonne 4 : Bouton supprimer
            delete_button = QPushButton("Supprimer")
            delete_button.clicked.connect(lambda _, hid=h.id: self.delete_history(hid))
            self.table.setCellWidget(row, 4, delete_button)

    def get_image_path(self, image_id):
        # Exemple : images/image_<id>.jpg
        return f"images/image_{image_id}.jpg" if image_id else ""

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
