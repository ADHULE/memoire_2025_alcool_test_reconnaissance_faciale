import sys
import serial
import serial.tools.list_ports
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                             QLabel, QComboBox, QPushButton, QTextEdit, QWidget,
                             QMessageBox)
from PySide6.QtCore import QTimer

class ArduinoSerialMonitor(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Moniteur Série Arduino")
        self.setGeometry(200, 200, 600, 400)

        self.serial_port = None
        self.baud_rate = 9600  # Vous pouvez rendre cela configurable
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.read_serial_data)
        self.is_connected = False

        # Widgets
        self.port_label = QLabel("Port Série:")
        self.port_combobox = QComboBox()
        self.refresh_button = QPushButton("Actualiser")
        self.connect_button = QPushButton("Connecter")
        self.disconnect_button = QPushButton("Déconnecter")
        self.data_display = QTextEdit()
        self.data_display.setReadOnly(True)

        # Layouts
        controls_layout = QHBoxLayout()
        controls_layout.addWidget(self.port_label)
        controls_layout.addWidget(self.port_combobox)
        controls_layout.addWidget(self.refresh_button)
        controls_layout.addWidget(self.connect_button)
        controls_layout.addWidget(self.disconnect_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(controls_layout)
        main_layout.addWidget(self.data_display)

        central_widget = QWidget(self)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Signaux et Slots
        self.refresh_button.clicked.connect(self.detect_ports)
        self.connect_button.clicked.connect(self.connect_serial)
        self.disconnect_button.clicked.connect(self.disconnect_serial)

        # Initialisation
        self.detect_ports()
        self.update_connection_status()

    def detect_ports(self):
        """Détecte et affiche les ports série disponibles."""
        self.port_combobox.clear()
        ports = serial.tools.list_ports.comports()
        arduino_ports = [p.device for p in ports if 'Arduino' in p.description]

        if arduino_ports:
            self.port_combobox.addItems(arduino_ports)
            if not self.is_connected and arduino_ports:
                QMessageBox.information(self, "Info", "Carte Arduino détectée. Sélectionnez un port et connectez-vous.")
        else:
            self.port_combobox.addItem("Aucun port Arduino détecté")
            if not self.is_connected:
                QMessageBox.warning(self, "Avertissement", "Aucune carte Arduino détectée. Assurez-vous qu'elle est connectée.")

        self.update_connection_status()

    def connect_serial(self):
        """Connecte au port série sélectionné."""
        selected_port = self.port_combobox.currentText()
        if selected_port and "Aucun port Arduino détecté" not in selected_port:
            try:
                self.serial_port = serial.Serial(selected_port, self.baud_rate)
                self.is_connected = True
                self.timer.start(100)  # Lire les données toutes les 100 ms
                QMessageBox.information(self, "Connecté", f"Connecté au port {selected_port}")
            except serial.SerialException as e:
                QMessageBox.critical(self, "Erreur de connexion", f"Impossible de se connecter à {selected_port}: {e}")
        else:
            QMessageBox.warning(self, "Avertissement", "Veuillez sélectionner un port Arduino.")
        self.update_connection_status()

    def disconnect_serial(self):
        """Déconnecte du port série."""
        if self.serial_port and self.serial_port.is_open:
            self.timer.stop()
            self.serial_port.close()
            self.serial_port = None
            self.is_connected = False
            QMessageBox.information(self, "Déconnecté", "Déconnecté du port série.")
        self.update_connection_status()

    def read_serial_data(self):
        """Lit les données du port série et les affiche."""
        if self.serial_port and self.serial_port.is_open:
            try:
                if self.serial_port.in_waiting > 0:
                    data = self.serial_port.readline().decode('utf-8').rstrip()
                    self.data_display.append(data)
                    self.data_display.ensureCursorVisible()  # Auto-scroll
            except serial.SerialException as e:
                self.data_display.append(f"Erreur de lecture série: {e}")
                self.disconnect_serial()
            except UnicodeDecodeError:
                self.data_display.append("Erreur de décodage des données série.")
                self.disconnect_serial()

    def update_connection_status(self):
        """Met à jour l'état des boutons de connexion/déconnexion."""
        self.connect_button.setEnabled(not self.is_connected and self.port_combobox.currentText() != "Aucun port Arduino détecté" and self.port_combobox.count() > 0)
        self.disconnect_button.setEnabled(self.is_connected)

# Lancer l'application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ArduinoSerialMonitor()
    window.show()
    sys.exit(app.exec())