import sys
from PySide6.QtWidgets import*
from PySide6.QtGui import*
from PySide6.QtCore import *

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Modern Desktop Application")
        self.setGeometry(100, 100, 1024, 768)

        # Création de la barre de menu
        self.menu_bar = self.menuBar()
        self.file_menu = self.menu_bar.addMenu("File")
        self.edit_menu = self.menu_bar.addMenu("Edit")
        self.view_menu = self.menu_bar.addMenu("View")
        self.help_menu = self.menu_bar.addMenu("Help")

        # Ajout d'actions au menu
        self.new_action = QAction("New", self)
        self.open_action = QAction("Open", self)
        self.save_action = QAction("Save", self)
        self.exit_action = QAction("Exit", self)
        self.file_menu.addAction(self.new_action)
        self.file_menu.addAction(self.open_action)
        self.file_menu.addAction(self.save_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.exit_action)

        # Création de la barre d'outils
        self.tool_bar = QToolBar("Main Toolbar")
        self.addToolBar(self.tool_bar)
        self.tool_bar.addAction(self.new_action)
        self.tool_bar.addAction(self.open_action)
        self.tool_bar.addAction(self.save_action)
        self.tool_bar.addSeparator()

        # Création du widget principal avec un QStackedWidget pour la réactivité
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Création des pages de contenu
        self.create_pages()

        # Connexion de l'action de sortie
        self.exit_action.triggered.connect(self.close)

    def create_pages(self):
        # Page d'accueil
        home_widget = QWidget()
        home_layout = QVBoxLayout()
        home_layout.addWidget(QLabel("Welcome to the Modern Desktop Application!"))
        home_widget.setLayout(home_layout)

        # Page des paramètres
        settings_widget = QWidget()
        settings_layout = QVBoxLayout()
        settings_layout.addWidget(QLabel("Settings Page"))
        settings_widget.setLayout(settings_layout)

        # Ajout des pages au QStackedWidget
        self.stacked_widget.addWidget(home_widget)
        self.stacked_widget.addWidget(settings_widget)

        # Création d'un QTabWidget pour d'autres éléments
        tab_widget = QTabWidget()
        tab1 = QWidget()
        tab2 = QWidget()
        tab_layout1 = QVBoxLayout()
        tab_layout2 = QVBoxLayout()
        tab_layout1.addWidget(QLabel("Content of Tab 1"))
        tab_layout2.addWidget(QLabel("Content of Tab 2"))
        tab1.setLayout(tab_layout1)
        tab2.setLayout(tab_layout2)
        tab_widget.addTab(tab1, "Tab 1")
        tab_widget.addTab(tab2, "Tab 2")

        # Ajout du QTabWidget au layout principal
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.stacked_widget)
        main_layout.addWidget(tab_widget)
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Création d'un menu de navigation
        nav_button_home = QPushButton("Home")
        nav_button_settings = QPushButton("Settings")
        nav_button_home.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(home_widget))
        nav_button_settings.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(settings_widget))

        # Ajout des boutons de navigation à la barre d'outils
        self.tool_bar.addWidget(nav_button_home)
        self.tool_bar.addWidget(nav_button_settings)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
