from PySide6.QtWidgets import QMainWindow, QLabel, QTextEdit, QVBoxLayout, QWidget
import json

class Mq3ValueGui(QMainWindow):
    def __init__(self, arduino_controller):
        super().__init__()
        self.setWindowTitle("MQ3 Alcohol Sensor Monitor")
        self.arduino_controller = arduino_controller

        # Créer un widget central pour le QMainWindow
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Créer les composants de l'interface
        self.status_label = QLabel("Microcontrôleur : 🔴 Déconnecté")
        self.status_label.setStyleSheet("font-weight: bold; color: red;")

        self.output_display = QTextEdit()
        self.output_display.setReadOnly(True)

        # Organiser les composants dans une mise en page verticale
        layout = QVBoxLayout()
        layout.addWidget(self.status_label)
        layout.addWidget(QLabel("Mesures en temps réel :"))
        layout.addWidget(self.output_display)
        central_widget.setLayout(layout)

        # Connexion des signaux du contrôleur Arduino
        self.arduino_controller.data_received.connect(self.on_data_received)

        # passer la fonction, pas son résultat
        self.arduino_controller.connection_status_changed.connect(self.update_status_label)

    def update_status_label(self, connected):
        """
        Met à jour l'étiquette de statut selon l'état de connexion.
        """
        if connected:
            self.status_label.setText("Microcontrôleur : 🟢 Connecté")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.status_label.setText("Microcontrôleur : 🔴 Déconnecté")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")

    def on_data_received(self, line):
        """
        Traite les données JSON reçues de l'Arduino et les affiche.
        """
        try:
            data = json.loads(line)
            msg = f"Alcool : {data['alcohol']}, État numérique : {data['digital']}, Alerte : {data['alert']}"
        except json.JSONDecodeError:
            msg = f"[Texte brut] {line}"
        self.output_display.append(msg)
