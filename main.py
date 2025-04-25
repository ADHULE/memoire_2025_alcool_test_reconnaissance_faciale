import sys
import os
from PySide6.QtWidgets import QApplication, QMessageBox
from Views.Home.main_window import MainWindow
from Views.Home.login_page import LoginWindow

if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        
        # Vérifier l'existence du fichier CSS avant de le charger
        css_path = "Styles/general_style.css"
        if os.path.exists(css_path):
            try:
                with open(css_path, "r") as file:
                    app.setStyleSheet(file.read())
            except Exception as e:
                error_message = f"Failed to load stylesheet: {e}"
                print(error_message)
                QMessageBox.warning(None, "Warning", error_message)
        else:
            print(f"Stylesheet not found at {css_path}")
            QMessageBox.warning(None, "Warning", f"Stylesheet not found at {css_path}")
        
        # Instanciation des fenêtres
        window = MainWindow()
        login = LoginWindow()

        # Connexion des signaux
        login.home_page_signal.connect(window.show)
        window.login_signal.connect(login.show)

        # Afficher la fenêtre de connexion
        login.show()
        sys.exit(app.exec())
    except Exception as e:
        error_message = f"An unexpected error occurred: {e}"
        print(error_message)
        QMessageBox.critical(None, "Critical Error", error_message)
