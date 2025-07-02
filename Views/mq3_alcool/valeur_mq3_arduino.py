from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QWidget, QTextEdit, QPushButton, QVBoxLayout,
    QLabel, QMessageBox, QComboBox, QHBoxLayout
)
from Controllers.arduino_controller import ArduinoController


class ArduinoValueView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Widgets UI
        self.output_display = QTextEdit()
        self.output_display.setReadOnly(True)
        self.port_combobox = QComboBox()
        self.status_label = QLabel("Statut : Déconnecté")

        self.start_button = QPushButton("Démarrer")
        self.start_button.clicked.connect(self.start_reading)

        self.stop_button = QPushButton("Arrêter")
        self.stop_button.clicked.connect(self.stop_reading)
        self.stop_button.setEnabled(False)

        # Instancie le contrôleur Arduino
        self.arduino = ArduinoController(self.port_combobox, self.status_label)
        self.arduino.data_received.connect(self.display_data)

        # Timer désactivé pour laisser la lecture au thread série
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.arduino.detect_serial_ports)
        self.timer.start()

        # Mise en page
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Ports détectés :"))
        layout.addWidget(self.port_combobox)
        layout.addWidget(self.status_label)
        layout.addWidget(QLabel("Données Arduino en temps réel :"))
        layout.addWidget(self.output_display)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def start_reading(self):
        self.arduino.connect_to_arduino()
        if self.arduino.is_connected():
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
        else:
            QMessageBox.warning(self, "Erreur", "Aucun port série valide sélectionné.")

    def stop_reading(self):
        self.arduino.close_connection()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def display_data(self, line):
        self.output_display.append(line)
