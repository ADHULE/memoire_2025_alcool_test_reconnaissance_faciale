import sys
import os
from PySide6.QtWidgets import QApplication, QMessageBox
from Views.Home.main_window import MAINWINDOW
from Views.Home.login_page import LOGINWINDOW
from Views.Home.webcam_page import ACCER_WEBCAMERA
from Controllers.arduino_controller import ArduinoController
from Views.mq3_alcool.mq3_arduino_value_ui import Mq3ValueGui

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
            QMessageBox.warning(
                None, "Warning", f"Stylesheet not found at {css_path}")

        # Instanciation des fenêtres
        window = MAINWINDOW()
        arduino_controller = ArduinoController()
        login = LOGINWINDOW(arduino_controller)
        webcam = ACCER_WEBCAMERA()
        arduino=Mq3ValueGui(arduino_controller)

        # Connexion des signaux
        login.home_page_signal.connect(window.show)
        login.webcam_page_signal.connect(webcam.show)
        window.login_signal.connect(login.show)
        webcam.mainwindow_signal.connect(window.show)
        login.arduino_value_signal.connect(arduino.show)

        # Afficher la fenêtre de connexion
        login.show()
        sys.exit(app.exec())
    except Exception as e:
        error_message = f"An unexpected error occurred: {e}"
        print(error_message)
        QMessageBox.critical(None, "Critical Error", error_message)
