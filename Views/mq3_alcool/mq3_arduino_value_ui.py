from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit
import json

class Mq3ValueGui(QWidget):
    def __init__(self, arduino_controller):
        super().__init__()
        self.setWindowTitle("MQ3 Alcohol Sensor Monitor")
        self.arduino_controller = arduino_controller

        # Connecter les signaux
        self.arduino_controller.data_received.connect(self.on_data_received)
        self.arduino_controller.connection_status_changed.connect(self.update_status_label)

        # Interface
        self.status_label = QLabel("Microcontrôleur : 🔴 Déconnecté")
        self.status_label.setStyleSheet("font-weight: bold; color: red;")
        self.output_display = QTextEdit()
        self.output_display.setReadOnly(True)

        layout = QVBoxLayout()
        layout.addWidget(self.status_label)
        layout.addWidget(QLabel("Mesures en temps réel :"))
        layout.addWidget(self.output_display)
        self.setLayout(layout)

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
            msg = f"Alcool : {data['alcohol']}, État numérique : {data['digital']}, Alerte : {data['alert']}"
        except json.JSONDecodeError:
            msg = f"[Texte brut] {line}"
        self.output_display.append(msg)
