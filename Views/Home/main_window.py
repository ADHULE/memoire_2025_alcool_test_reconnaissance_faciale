from PySide6.QtWidgets import QMainWindow, QTabWidget, QStackedWidget, QToolButton, QMenu, QPushButton
from PySide6.QtCore import Signal, Qt
import functools

# Importation des différentes pages
from Views.chauffeur.chauffeur_view import Chauffeur_View


class MainWindow(QMainWindow):
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
            "Driver": Chauffeur_View(parent=self),
        }

        # Gérer les différentes pages filles qui ne sont pas directement affichées dans la page principale
        self.stack_widget = QStackedWidget()

        # Créer les onglets
        self.create_tabs()

        # Créer le bouton de menu (pour les écrans étroits)
        self.menu_button = QToolButton(self)
        self.menu_button.setPopupMode(QToolButton.InstantPopup)
        self.menu_button.setMenu(QMenu(self.menu_button))
        self.menu_button.setVisible(False)

        # ✅ **Ajout du bouton de déconnexion**
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
                action.triggered.connect(functools.partial(self.tab_widget.setCurrentIndex, i))

        super().resizeEvent(event)

    def back_to_login_page(self):
        """
        Émet le signal pour retourner à la page de connexion et ferme la fenêtre principale.
        """
        self.login_signal.emit()
        self.close()

    def navigate_to(self, page_name):
        """
        Permet de naviguer vers une page spécifique.
        """
        if page_name in self.pages:
            self.tab_widget.setCurrentWidget(self.pages[page_name])
        else:
            print(f"Page '{page_name}' non trouvée.")
