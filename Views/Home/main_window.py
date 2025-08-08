import functools
import os

from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon, QFont, QPixmap
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QStackedWidget, QMessageBox, QFrame, QLabel, QSpacerItem, QSizePolicy
)

from Controllers.arduino_controller import ArduinoController
# Importation des différentes pages
from Views.admin.enregistrer import ENREGISTREMENT_ADMIN
from Views.admin.modifier import MODIFIER_ADMIN
from Views.chauffeur.enregistrer import ENREGISTREMENT_CHAUFFEUR
from Views.chauffeur.modifier import MODIFIER_CHAUFFEUR
from Views.historique.display_history import DISPLAY_HISTORY
from Views.image.image_view import IMAGE_VIEW
from Views.image.modifier_photo import MODIFIER_IMAGES_PAGE
from Views.image.photo_display import DISPLAY_IMAGES
# from Views.mq3_alcool.alcool_mananger import AlcoolDataManager



class MAINWINDOW(QMainWindow):
    # Signal pour retourner à la page de connexion
    login_signal = Signal()

    def __init__(self):
        super().__init__()

        self.setWindowTitle("GESTION DES INFORMATIONS")
        # self.setMinimumSize(1000, 700) # Adjusted minimum size for new layout

        self.arduino_controller = ArduinoController()

        # Initialize pages dictionary with instances
        self.pages = {
            "Gestion des administrateurs": ENREGISTREMENT_ADMIN(parent=self),
            "Gestion des chauffeurs": ENREGISTREMENT_CHAUFFEUR(parent=self),
            "Ajouter les images": IMAGE_VIEW(parent=self),
            "Afficher les images": DISPLAY_IMAGES(parent=self),
            "Voir les historiques": DISPLAY_HISTORY(parent=self),
            # "Alcool_Manager":AlcoolDataManager()
        }

        self._setup_ui()
        self._load_stylesheet("Styles/main_window_styles.css")

    def _load_stylesheet(self, path: str):

        try:
            with open(path, "r") as file:
                self.setStyleSheet(file.read())
        except FileNotFoundError:
            QMessageBox.warning(self, "Erreur", f"Feuille de style non trouvée : {path}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de charger la feuille de style : {e}")

    def _setup_ui(self):

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0) # No margins for the main layout
        main_layout.setSpacing(0) # No spacing between sidebar and content


        self.sidebar_frame = QFrame()
        self.sidebar_frame.setObjectName("sidebarFrame")
        self.sidebar_frame.setFixedWidth(300) # Fixed width for the sidebar
        sidebar_layout = QVBoxLayout(self.sidebar_frame)
        sidebar_layout.setContentsMargins(10, 10, 10, 10)
        sidebar_layout.setSpacing(10)

        # Application Logo/Title
        logo_label = QLabel()
        logo_pixmap = QPixmap("icons/app_logo.png").scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation) # Placeholder
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setObjectName("appLogo")
        sidebar_layout.addWidget(logo_label)

        app_title = QLabel("Menu Principal")
        app_title.setAlignment(Qt.AlignCenter)
        app_title.setObjectName("appTitle")
        sidebar_layout.addWidget(app_title)
        sidebar_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed)) # Spacer

        # Navigation Buttons
        self.nav_buttons = {}
        for page_name, page_instance in self.pages.items():
            button = QPushButton(page_name)
            button.setObjectName("navButton")
            button.setIcon(self._get_icon_for_page(page_name)) # Set icon
            button.setIconSize(QSize(24, 24))

            button.clicked.connect(functools.partial(self.show_page, page_instance))
            sidebar_layout.addWidget(button)
            self.nav_buttons[page_name] = button

        sidebar_layout.addStretch()


        self.logout_button = QPushButton("Déconnexion")
        self.logout_button.setObjectName("logoutButton")
        self.logout_button.setIcon(QIcon("Icons/logout.png"))
        self.logout_button.setIconSize(QSize(24, 24))
        self.logout_button.clicked.connect(self.back_to_login_page)
        sidebar_layout.addWidget(self.logout_button)

        main_layout.addWidget(self.sidebar_frame)

        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setObjectName("contentArea")
        main_layout.addWidget(self.stacked_widget)


        for page_name, page_instance in self.pages.items():
            self.stacked_widget.addWidget(page_instance)


        self.show_page(self.pages["Gestion des administrateurs"])

    def _get_icon_for_page(self, page_name: str) -> QIcon:

        icon_map = {
            "Gestion des administrateurs": "Icons/admin.png",
            "Gestion des chauffeurs": "Icons/driver_icon.png",
            "Ajouter les images": "Icons/add_image_icon.png",
            "Afficher les images": "Icons/view_image_icon.png",
            "Voir les historiques": "Icons/history_icon.png",

            # Add more mappings as needed
        }
        path = icon_map.get(page_name, "icons/default_icon.png") # Default icon if not found
        return QIcon(path)

    def show_page(self, page_instance: QWidget):

        self.stacked_widget.setCurrentWidget(page_instance)

        # Update button styling to indicate active page
        for name, button in self.nav_buttons.items():
            if self.pages[name] == page_instance:
                button.setProperty("active", True)
            else:
                button.setProperty("active", False)
            button.style().polish(button) # Repolish to apply stylesheet changes


    def back_to_login_page(self):

        confirmation = QMessageBox.question(
            self, "Confirmation", "Voulez-vous vraiment vous déconnecter ?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirmation == QMessageBox.Yes:
            try:
                # Disconnect any active camera streams or Arduino connections before closing
                if "Caméra" in self.pages and hasattr(self.pages["Caméra"], 'camera_controller'):
                    self.pages["Caméra"].camera_controller.stop_camera()
                if self.arduino_controller.is_connected():
                    self.arduino_controller.close_connection()

                self.login_signal.emit()
                self.close()
            except Exception as e:
                QMessageBox.critical(self, "Erreur de Déconnexion",
                                     f"Une erreur est survenue lors de la déconnexion : {str(e)}")



    def open_modify_photo_page(self, id_photo):

        modifier_photo = MODIFIER_IMAGES_PAGE(id_photo, parent=self)
        modifier_photo.exec()

    def open_modify_admin_page(self, admin_id):

        modifier_admin = MODIFIER_ADMIN(admin_id, parent=self)
        modifier_admin.exec()

    def open_modify_chauffeur_page(self, chauffeur_id):

        modifier_chauffeur = MODIFIER_CHAUFFEUR(chauffeur_id, parent=self)
        modifier_chauffeur.exec()