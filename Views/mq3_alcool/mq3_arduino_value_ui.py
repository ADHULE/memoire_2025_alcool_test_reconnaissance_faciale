from PySide6.QtWidgets import QMainWindow, QLabel, QTextEdit, QVBoxLayout, QWidget
import json

class Mq3ValueGui(QMainWindow):
    def __init__(self, arduino_controller):
        super().__init__()
        self.setWindowTitle("MQ3 Alcohol Sensor Monitor")
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

        self.arduino_controller.data_received.connect(self.on_data_received)
        self.arduino_controller.connection_status_changed.connect(self.update_status_label)

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
            raw_value = float(data.get("alcohol", 0))
            normalized = round(raw_value / 1023.0, 3)
            alert = data.get("alert", False)

            # Choisir la couleur selon l'état de l'alerte
            couleur = "red" if alert else "green"

            msg_html = (
                f"<span style='color:{couleur};'>"
                f"Alcool brut : {raw_value} | "
                f"Alcool normalisé : {normalized} | "
                f"État numérique : {data.get('digital', 'N/A')} | "
                f"Alerte : {alert}"
                f"</span>"
            )
        except (json.JSONDecodeError, ValueError) as e:
            msg_html = f"<span style='color:orange;'>[Erreur] Ligne non valide : {line} ({e})</span>"

        self.output_display.append(msg_html)
