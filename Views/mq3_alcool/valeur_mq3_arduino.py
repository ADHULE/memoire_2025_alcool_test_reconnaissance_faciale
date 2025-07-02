import sys
import serial
import serial.tools.list_ports
import json

from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTextEdit, QLabel, QComboBox, QMessageBox
)

class MQ3MinimalGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MQ3 Alcohol Sensor Monitor")
        self.serial_connection = None

        # Widgets
        self.port_combobox = QComboBox()
        self.refresh_button = QPushButton("🔄 Actualiser ports")
        self.connect_button = QPushButton("Connexion")
        self.disconnect_button = QPushButton("Déconnexion")
        self.status_label = QLabel("Statut : Déconnecté")
        self.output_display = QTextEdit()
        self.output_display.setReadOnly(True)
        self.led_on_btn = QPushButton("Allumer LED")
        self.led_off_btn = QPushButton("Éteindre LED")

        # Disposition
        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("Port série :"))
        top_layout.addWidget(self.port_combobox)
        top_layout.addWidget(self.refresh_button)

        ctrl_layout = QHBoxLayout()
        ctrl_layout.addWidget(self.connect_button)
        ctrl_layout.addWidget(self.disconnect_button)
        ctrl_layout.addWidget(self.led_on_btn)
        ctrl_layout.addWidget(self.led_off_btn)

        layout = QVBoxLayout()
        layout.addLayout(top_layout)
        layout.addWidget(self.status_label)
        layout.addLayout(ctrl_layout)
        layout.addWidget(QLabel("Mesures en temps réel :"))
        layout.addWidget(self.output_display)
        self.setLayout(layout)

        # Connexions
        self.refresh_button.clicked.connect(self.refresh_ports)
        self.connect_button.clicked.connect(self.connect_serial)
        self.disconnect_button.clicked.connect(self.disconnect_serial)
        self.led_on_btn.clicked.connect(lambda: self.send_command("LED_ON\n"))
        self.led_off_btn.clicked.connect(lambda: self.send_command("LED_OFF\n"))

        # Timer pour lire les données
        self.read_timer = QTimer(self)
        self.read_timer.timeout.connect(self.read_data)

        self.refresh_ports()

    def refresh_ports(self):
        self.port_combobox.clear()
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.port_combobox.addItem(port.device)

    def connect_serial(self):
        port = self.port_combobox.currentText()
        if not port:
            QMessageBox.warning(self, "Erreur", "Aucun port sélectionné.")
            return
        try:
            self.serial_connection = serial.Serial(port, baudrate=9600, timeout=1)
            self.status_label.setText(f"🟢 Connecté à {port}")
            self.status_label.setStyleSheet("color: green;")
            self.read_timer.start(300)
        except serial.SerialException as e:
            QMessageBox.critical(self, "Erreur de connexion", str(e))

    def disconnect_serial(self):
        self.read_timer.stop()
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
        self.status_label.setText("🔴 Déconnecté")
        self.status_label.setStyleSheet("color: red;")

    def read_data(self):
        try:
            if self.serial_connection.in_waiting:
                raw = self.serial_connection.readline().decode().strip()
                try:
                    data = json.loads(raw)
                    msg = f"Alcool : {data['alcohol']}, État numérique : {data['digital']}, Alerte : {data['alert']}"
                    self.output_display.append(msg)
                except json.JSONDecodeError:
                    self.output_display.append(f"[Texte brut] {raw}")
        except Exception as e:
            self.output_display.append(f"[Erreur] {e}")

    def send_command(self, cmd):
        if self.serial_connection and self.serial_connection.is_open:
            try:
                self.serial_connection.write(cmd.encode())
            except Exception as e:
                self.output_display.append(f"[Erreur d'envoi] {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = MQ3MinimalGUI()
    gui.resize(500, 400)
    gui.show()
    sys.exit(app.exec())
