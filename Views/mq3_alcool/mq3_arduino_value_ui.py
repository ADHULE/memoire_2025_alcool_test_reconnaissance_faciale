from PySide6.QtWidgets import QMainWindow, QLabel, QTextEdit, QVBoxLayout, QWidget
from datetime import datetime
import json

# ✅ Import du contrôleur base de données
from Controllers.alcool_test_controller import AlcoolTestController

class Mq3ValueGui(QMainWindow):
    def __init__(self, arduino_controller):
        super().__init__()
        self.setWindowTitle("LECTURE DE LA VALEUR DE CAPTEUR D'ALCOOL")
        self.arduino_controller = arduino_controller

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.status_label = QLabel("Microcontrôleur : 🔴 Déconnecté")
        self.status_label.setStyleSheet("font-weight: bold; color: red;")

        self.output_display = QTextEdit()
        self.output_display.setReadOnly(True)

        layout = QVBoxLayout()
        layout.addWidget(self.status_label)
        layout.addWidget(QLabel("Mesures en temps réel :"))
        layout.addWidget(self.output_display)
        central_widget.setLayout(layout)

        # Connexions de signaux
        self.arduino_controller.data_received.connect(self.on_data_received)
        self.arduino_controller.connection_status_changed.connect(self.update_status_label)

        #Initialisation du contrôleur de base
        self.database_controller = AlcoolTestController()
        self.arduino_controller.set_database_controller(self.database_controller)

    def update_status_label(self, connected):
        if connected:
            self.status_label.setText("Microcontrôleur : 🟢 Connecté")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.status_label.setText("Microcontrôleur : 🔴 Déconnecté")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")

    def on_data_received(self, line):
        try:
            data = json.loads(line)

            # ✅ Vérifie présence de la clé "alcohol"
            if "alcohol" not in data:
                raise ValueError("Donnée 'alcohol' manquante dans la ligne reçue.")

            raw_value = float(data["alcohol"])
            normalized = round(raw_value / 1023.0, 3)
            alert = bool(data.get("alert", False))
            seuil_detection = 400  #  seuil critique à ajuster selon les tests

            couleur = "red" if alert else "green"
            msg_html = (
                f"<span style='color:{couleur};'>"
                # f"Alcool brut : {raw_value} | "
                f"{normalized} mg/L"
                # f"  Alerte : {alert}"
                f"</span>"
            )

            # Si alerte active ET brut > seuil
            if alert and raw_value > seuil_detection:
                try:
                    self.arduino_controller.db_controller.new_alcool_value(datetime.now(), raw_value)
                    print(f"[INFO] Valeur brute enregistrée avec alerte : {raw_value}")
                except Exception as e:
                    # return f"{e}"
                    print(f"[DB ERROR] Échec d'enregistrement (alerte) : {e}")

            #  Optionnel : enregistre valeur normalisée si > 0 (hors alerte)
            elif normalized > 0:
                try:
                    self.arduino_controller.db_controller.new_alcool_value(datetime.now(), normalized)
                    print(f"[INFO] Valeur normalisée enregistrée : {normalized}")
                except Exception as e:
                    print(f"[DB ERROR] Échec d'enregistrement (normalisée) : {e}")

        except (json.JSONDecodeError, ValueError) as e:
            msg_html = f"<span style='color:orange;'>[Erreur] Ligne non valide : {line} ({e})</span>"

        self.output_display.append(msg_html)
