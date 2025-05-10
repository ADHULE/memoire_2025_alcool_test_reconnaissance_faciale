from PySide6.QtWidgets import *
from PySide6.QtCore import *
import functools

# Importation des différentes pages
from Views.chauffeur.enregistrer import ENREGISTREMENT_CHAUFFEUR
from Views.chauffeur.modifier import MODIFIER_CHAUFFEUR
from Views.image.image_view import IMAGE_VIEW
from Views.image.photo_display import DISPLAY_IMAGES
from Views.image.modifier_photo import MODIFIER_IMAGES_PAGE
from Views.admin.enregistrer import ENREGISTREMENT_ADMIN
from Views.admin.modifier import MODIFIER_ADMIN
from Views.historique.display_history import DISPLAY_HISTORY


class MAINWINDOW(QMainWindow):
    # Signal pour retourner à la page de connexion
    login_signal = Signal()

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Application de Gestion Académique")

        # Créer le widget d'onglets
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        # Ajouter les différentes pages à l'onglet
        self.pages = {
            "Admin":ENREGISTREMENT_ADMIN(parent=self),
            "Driver": ENREGISTREMENT_CHAUFFEUR(parent=self),
            "Add Images": IMAGE_VIEW(parent=self),
            "Display Images": DISPLAY_IMAGES(parent=self),
            "Display History":DISPLAY_HISTORY(parent=self)
                
        }

        # Créer les onglets
        self.create_tabs()

        # Créer le bouton de menu (pour les écrans étroits)
        self.menu_button = QToolButton(self)
        self.menu_button.setPopupMode(QToolButton.InstantPopup)
        self.menu_button.setMenu(QMenu(self.menu_button))
        self.menu_button.setVisible(False)

        # Ajout du bouton de déconnexion
        self.logout_button = QPushButton("Déconnexion")
        self.logout_button.clicked.connect(self.back_to_login_page)
        self.tab_widget.setCornerWidget(self.logout_button, Qt.TopRightCorner)

        # Connecter le signal de changement d'onglet
        self.tab_widget.currentChanged.connect(self.on_tab_changed)

    def create_tabs(self):
        """
        Ajoute les pages aux onglets du widget tabulaire.
        """
        for page_name, page in self.pages.items():
            self.tab_widget.addTab(page, page_name)

    def on_tab_changed(self, index):
        """
        Gère l'affichage du bouton de menu en fonction de l'onglet actif.
        """
        self.menu_button.setVisible(index == 2)

    def resizeEvent(self, event):
        """
        Ajuste l'affichage des onglets et du bouton de menu en fonction de la taille de la fenêtre.
        """
        is_narrow = event.size().width() < 600
        self.tab_widget.tabBar().setVisible(not is_narrow)
        self.menu_button.setVisible(is_narrow)

        if is_narrow:
            self.menu_button.menu().clear()
            for i in range(self.tab_widget.count()):
                action = self.menu_button.menu().addAction(self.tab_widget.tabText(i))
                action.triggered.connect(
                    functools.partial(self.tab_widget.setCurrentIndex, i)
                )

        super().resizeEvent(event)

    def back_to_login_page(self):
        """
        Émet le signal pour retourner à la page de connexion et ferme la fenêtre principale.
        """
        confirmation = QMessageBox.question(
            self, "Confirmation", " Voulez vous vraiment vous deconnecter?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirmation == QMessageBox.Yes:
            try:

                self.login_signal.emit()
                self.close()
            except  Exception as e:
                QMessageBox.information(f"Erreur lors de la deconnection {str(e)}")
    def navigate_to(self, page_name):
        """
        Permet de naviguer vers une page spécifique.
        """
        if page_name in self.pages:
            self.tab_widget.setCurrentWidget(self.pages[page_name])
        else:
            print(f"Page '{page_name}' non trouvée.")


    """__________________________NAVIGATION ENTRE VERS LES PAGES________________________"""

    def open_modify_photo_page(self, id_photo):
            modifier_photo = MODIFIER_IMAGES_PAGE(id_photo)
            modifier_photo.exec()

    def open_modify_admin_page(self, admin_id):
            modifier_photo = MODIFIER_ADMIN(admin_id)
            modifier_photo.exec()

    def open_modify_chauffeur_page(self, chauffeur_id):
            modifier_photo = MODIFIER_CHAUFFEUR(chauffeur_id)
            modifier_photo.exec()
