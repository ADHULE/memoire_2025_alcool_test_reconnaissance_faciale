import sys
import serial.tools.list_ports
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QComboBox, QLabel, QTextEdit, QWidget

class ArduinoPortScanner(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Détection et Connexion à Arduino")
        self.setGeometry(200, 200, 500, 250)

        # Widget principal
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Layout vertical
        layout = QVBoxLayout(central_widget)

        # ComboBox pour afficher les ports détectés
        self.port_combobox = QComboBox()
        layout.addWidget(QLabel("Ports disponibles :"))
        layout.addWidget(self.port_combobox)

        # Zone de texte pour afficher les informations sur le port
        self.port_info = QTextEdit()
        self.port_info.setReadOnly(True)
        layout.addWidget(QLabel("Informations du port :"))
        layout.addWidget(self.port_info)

        # Bouton pour actualiser la liste des ports
        self.refresh_button = QPushButton("Actualiser les ports")
        self.refresh_button.clicked.connect(self.detect_ports)
        layout.addWidget(self.refresh_button)

        # Bouton pour connecter à Arduino
        self.connect_button = QPushButton("Connecter à Arduino")
        self.connect_button.clicked.connect(self.connect_to_arduino)
        layout.addWidget(self.connect_button)

        # Indicateur de statut
        self.status_label = QLabel("Statut : Déconnecté")
        layout.addWidget(self.status_label)

        # Détecter les ports lors du démarrage
        self.detect_ports()

    def detect_ports(self):
        """Méthode pour détecter et afficher les ports série."""
        self.port_combobox.clear()
        self.port_info.clear()
        ports = serial.tools.list_ports.comports()

        for port in ports:
            self.port_combobox.addItem(port.device)  # Ajouter chaque port détecté

            # Afficher les détails du port dans la console
            print(f"Port détecté : {port.device} | Description : {port.description} | VID/PID : {port.hwid}")

            # Ajouter les détails dans l'interface graphique
            self.port_info.append(f"Port : {port.device}\nDescription : {port.description}\nVID/PID : {port.hwid}\n")

    def connect_to_arduino(self):
        """Essayer de se connecter à Arduino."""
        selected_port = self.port_combobox.currentText()
        if selected_port:
            try:
                arduino = serial.Serial(selected_port, baudrate=9600, timeout=1)
                self.status_label.setText(f"Statut : Connecté à {selected_port}")
                print(f"Connexion réussie sur {selected_port} !")
                arduino.close()
            except Exception as e:
                self.status_label.setText(f"Statut : Erreur de connexion")
                print(f"Erreur lors de la connexion : {e}")

# Lancer l'application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ArduinoPortScanner()
    window.show()
    sys.exit(app.exec())
