import json
from PySide6.QtWidgets import QMainWindow, QLabel, QTextEdit, QVBoxLayout, QWidget
from Controllers.alcool_test_controller import AlcoolTestController

class Mq3ValueGui(QMainWindow):
    def __init__(self, arduino_controller):
        super().__init__()
        self.setWindowTitle("LECTURE DE LA VALEUR DE CAPTEUR D'ALCOOL")
        self.arduino_controller = arduino_controller

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.status_label = QLabel("Microcontrôleur : Déconnecté")
        self.status_label.setStyleSheet("font-weight: bold; color: red;")

        self.output_display = QTextEdit()
        self.output_display.setReadOnly(True)

        self.save_alcool_value = None

        layout = QVBoxLayout()
        layout.addWidget(self.status_label)
        layout.addWidget(QLabel("Mesures en temps réel :"))
        layout.addWidget(self.output_display)
        central_widget.setLayout(layout)

        self.arduino_controller.data_received.connect(self.on_data_received)
        self.arduino_controller.connection_status_changed.connect(self.update_status_label)

        self.database_controller = AlcoolTestController()
        self.arduino_controller.set_database_controller(self.database_controller)

    def update_status_label(self, connected):
        if connected:
            self.status_label.setText("Microcontrôleur : Connecté")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.status_label.setText("Microcontrôleur :  Déconnecté")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")

    def on_data_received(self, line):
        try:
            data = json.loads(line)

            if "alcohol" not in data:
                raise ValueError("Donnée 'alcohol' manquante.")

            raw_value = float(data["alcohol"])
            normalized = round(raw_value / 1023.0, 3)
            alert = bool(data.get("alert", False))
            seuil_detection = 400

            couleur = "red" if alert else "green"
            msg_html = f"<span style='color:{couleur};'>{normalized} mg/L</span>"

            if alert and raw_value > seuil_detection:
                self.save_alcool_value = raw_value
            elif normalized > 0:
                print(f"[INFO] Valeur normalisée enregistrée : {normalized}")

        except (json.JSONDecodeError, ValueError) as e:
            msg_html = f"<span style='color:orange;'>[Erreur] Ligne non valide : {line} ({e})</span>"

        self.output_display.append(msg_html)

    def _save_alcool_value(self):
        return self.save_alcool_value
