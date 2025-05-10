from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from Controllers.historique_controller import HISTORIQUE_CONTROLLER
import logging

class DISPLAY_HISTORY(QWidget):
    """
    Widget pour afficher et gérer l'historique des événements.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Historique des événements")
        self.parent = parent

        # Initialisation des objets
        self.history_controller = HISTORIQUE_CONTROLLER()
        self.all_history = []

        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
        self.logger = logging.getLogger(__name__)

        self.setup_ui()
        # QTimer.singleShot(0, self.load_history_from_controller)

    def setup_ui(self):
        """Configure l'interface utilisateur pour l'affichage de l'historique."""
        main_layout = QVBoxLayout()

        # Barre d'outils supérieure
        toolbar_layout = QHBoxLayout()
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Rechercher par type d'événement")
        self.search_edit.textChanged.connect(self.filter_history)
        toolbar_layout.addWidget(self.search_edit)

        self.refresh_button = QPushButton("Actualiser")
        self.refresh_button.clicked.connect(self.load_history_from_controller)
        toolbar_layout.addWidget(self.refresh_button)

        main_layout.addLayout(toolbar_layout)

        # Zone d'affichage des événements historiques
        self.history_list_widget = QListWidget()
        main_layout.addWidget(self.history_list_widget)

        self.setLayout(main_layout)

    def load_history_from_controller(self):
        """Charge l'historique depuis le contrôleur et l'affiche."""
        try:
            self.all_history = self.history_controller.get_histories()
            self._display_history(self.all_history)
        except Exception as e:
            self.logger.error(f"Erreur lors du chargement de l'historique: {e}")
            self.show_message("Erreur", "Impossible de charger l'historique.")

    def _display_history(self, histories):
        """Affiche les événements historiques dans la liste."""
        self.history_list_widget.clear()
        for history in histories:
            item = QListWidgetItem(f"{history.jour_heure} - {history.event_type}")
            self.history_list_widget.addItem(item)

    def filter_history(self, text):
        """Filtre l'historique affiché en fonction du type d'événement."""
        if not text:
            self._display_history(self.all_history)
            return
        filtered_histories = [h for h in self.all_history if text.lower() in h.event_type.lower()]
        self._display_history(filtered_histories)

    def show_message(self, title, message):
        """Affiche une boîte de message informative."""
        QMessageBox.information(self, title, message)
