import functools

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from Controllers.arduino_controller import ArduinoController
from Views.admin.enregistrer import ENREGISTREMENT_ADMIN
from Views.admin.modifier import MODIFIER_ADMIN
# Importation des différentes pages
# Assurez-vous que ces imports sont corrects et que les fichiers existent
from Views.chauffeur.enregistrer import ENREGISTREMENT_CHAUFFEUR
from Views.chauffeur.modifier import MODIFIER_CHAUFFEUR
from Views.historique.display_history import DISPLAY_HISTORY
from Views.image.image_view import IMAGE_VIEW
from Views.image.modifier_photo import MODIFIER_IMAGES_PAGE
from Views.image.photo_display import DISPLAY_IMAGES



class MAINWINDOW(QMainWindow):
    # Signal pour retourner à la page de connexion
    login_signal = Signal()

    def __init__(self):
        super().__init__()

        self.setWindowTitle("GESTION DE DECTEUR D'ALCOOL ET RECONNAISSANCE FACIALE")
        # icon_path = os.path.abspath("Images/Logo.ico")
        # self.setWindowIcon(QIcon(icon_path))
        self.setMinimumSize(800, 600)  # Suggestion: Set a minimum size for better initial display

        # Créer le widget d'onglets
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        # Ajouter les différentes pages à l'onglet
        # Il est important de passer 'self' comme parent si les pages ont besoin d'interagir avec la fenêtre principale

        self.arduino_controller = ArduinoController()

        self.pages = {
            "Gestion Admins": ENREGISTREMENT_ADMIN(parent=self),
            "Gestion Chauffeurs": ENREGISTREMENT_CHAUFFEUR(parent=self),
            "Ajouter Images": IMAGE_VIEW(parent=self),
            "Afficher Images": DISPLAY_IMAGES(parent=self),
            "Historique": DISPLAY_HISTORY(parent=self),

        }
        # Créer les onglets
        self.create_tabs()

        # Créer le bouton de menu (pour les écrans étroits)
        self.menu_button = QToolButton(self)
        self.menu_button.setPopupMode(QToolButton.InstantPopup)
        self.menu_button.setMenu(QMenu(self.menu_button))
        # Initialement invisible, sera géré par resizeEvent et on_tab_changed
        self.menu_button.setVisible(False)

        # Ajout du bouton de déconnexion
        self.logout_button = QPushButton("Déconnexion")
        self.logout_button.clicked.connect(self.back_to_login_page)
        # Assurez-vous que le bouton de déconnexion est toujours visible
        self.tab_widget.setCornerWidget(self.logout_button, Qt.TopRightCorner)

        # Connecter le signal de changement d'onglet
        # Ceci permet de gérer la visibilité du menu_button si nécessaire
        self.tab_widget.currentChanged.connect(self.on_tab_changed)

    def create_tabs(self):
        """
        Ajoute les pages aux onglets du widget tabulaire.
        """
        for page_name, page in self.pages.items():
            self.tab_widget.addTab(page, page_name)

    def on_tab_changed(self, index):
        """
        Gère la logique spécifique lors du changement d'onglet si nécessaire.
        Vous pourriez vouloir ajuster le menu_button ici si son comportement dépend de l'onglet.
        Actuellement, il n'y a pas de logique spécifique ici qui rendrait le bouton de menu visible
        uniquement pour l'index 2. Le `resizeEvent` gère la visibilité basée sur la largeur.
        """
        # Si vous vouliez que le menu_button soit visible SEULEMENT pour un onglet spécifique (ex: index 2),
        # vous pourriez le réactiver ici, mais le `resizeEvent` le gère déjà.
        # self.menu_button.setVisible(self.is_narrow and index == 2)
        pass  # Pas de changement fonctionnel nécessaire ici pour le moment.

    def resizeEvent(self, event):
        """
        Ajuste l'affichage des onglets et du bouton de menu en fonction de la taille de la fenêtre.
        """
        # Mise à jour de l'état "is_narrow"
        is_narrow = event.size().width() < 600
        self.tab_widget.tabBar().setVisible(not is_narrow)

        # Le bouton de menu est visible si la fenêtre est étroite
        self.menu_button.setVisible(is_narrow)

        if is_narrow:
            # Reconstruire le menu à chaque redimensionnement en mode étroit
            # pour s'assurer qu'il reflète les onglets actuels.
            self.menu_button.menu().clear()
            for i in range(self.tab_widget.count()):
                action = self.menu_button.menu().addAction(self.tab_widget.tabText(i))
                # Utilisation de functools.partial pour s'assurer que le bon index est passé
                action.triggered.connect(functools.partial(self.tab_widget.setCurrentIndex, i))

        super().resizeEvent(event)

    def back_to_login_page(self):
        """
        Émet le signal pour retourner à la page de connexion et ferme la fenêtre principale.
        """
        confirmation = QMessageBox.question(
            self, "Confirmation", "Voulez-vous vraiment vous déconnecter ?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirmation == QMessageBox.Yes:
            try:
                self.login_signal.emit()  # Émet le signal pour que la logique externe prenne le relais
                self.close()  # Ferme cette fenêtre principale
            except Exception as e:
                # Correction: Le premier argument de QMessageBox.information doit être le parent
                QMessageBox.critical(self, "Erreur de Déconnexion",
                                     f"Une erreur est survenue lors de la déconnexion : {str(e)}")

    def navigate_to(self, page_name):
        """
        Permet de naviguer vers une page spécifique en utilisant son nom défini dans self.pages.
        """
        if page_name in self.pages:
            self.tab_widget.setCurrentWidget(self.pages[page_name])
        else:
            QMessageBox.warning(self, "Page Non Trouvée", f"La page '{page_name}' n'existe pas.")

    # --- NAVIGATION VERS LES PAGES DE MODIFICATION (Pop-up Dialogues) ---
    # Ces méthodes ouvrent des fenêtres de modification comme des dialogues modaux.

    def open_modify_photo_page(self, id_photo):
        """Ouvre la fenêtre de modification d'image."""
        # Passer 'self' comme parent à la fenêtre de modification est une bonne pratique
        modifier_photo = MODIFIER_IMAGES_PAGE(id_photo, parent=self)
        modifier_photo.exec()  # Ouvre comme un dialogue modal

    def open_modify_admin_page(self, admin_id):
        """Ouvre la fenêtre de modification d'administrateur."""
        modifier_admin = MODIFIER_ADMIN(admin_id, parent=self)
        modifier_admin.exec()

    def open_modify_chauffeur_page(self, chauffeur_id):
        """Ouvre la fenêtre de modification de chauffeur."""
        modifier_chauffeur = MODIFIER_CHAUFFEUR(chauffeur_id, parent=self)
        modifier_chauffeur.exec()

