import serial
import serial.tools.list_ports

from PySide6.QtCore import QObject, Signal, Slot, QTimer
from PySide6.QtWidgets import QMessageBox
from Controllers.alcool_test_controller import AlcoolTestController

class ArduinoController(QObject):
    data_received = Signal(str)
    connection_status_changed = Signal(bool)

    def __init__(self, port_combobox=None, status_label=None, seuil_ivresse=0.4):
        super().__init__()
        self.port_combobox = port_combobox
        self.status_label = status_label
        self.seuil_ivresse = seuil_ivresse
        self.serial_connection = None
        self.last_validated_alcohol_value = None

        # Timer pour lecture périodique
        self.read_timer = QTimer()
        self.read_timer.setInterval(200)  # lecture toutes les 200ms
        self.read_timer.timeout.connect(self._read_serial)

    def detect_serial_ports(self):
        if self.port_combobox:
            self.port_combobox.clear()
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if self.port_combobox:
                self.port_combobox.addItem(f"{port.device} - {port.description}")
        if not ports and self.port_combobox:
            self.port_combobox.addItem("Aucun port série détecté")

    def connect_to_arduino(self):
        if not self.port_combobox:
            self.connection_status_changed.emit(False)
            return

        selected = self.port_combobox.currentText()
        if " - " not in selected:
            self._update_status("Aucun port valide sélectionné", "red")
            self.connection_status_changed.emit(False)
            return

        port = selected.split(" - ")[0]
        try:
            self.serial_connection = serial.Serial(port, 9600, timeout=1)
            self._update_status(f"{port}", "green")
            self.port_combobox.clear()
            self.port_combobox.addItem(port)
            self.read_timer.start()
            self.connection_status_changed.emit(True)
        except serial.SerialException:
            self._update_status("Erreur de connexion", "red")
            self.connection_status_changed.emit(False)

    def _update_status(self, text, color):
        if self.status_label:
            self.status_label.setText(text)
            self.status_label.setStyleSheet(f"color: {color}; font-weight: bold;")

    def is_connected(self):
        return self.serial_connection and self.serial_connection.is_open

    @Slot()
    def _read_serial(self):
        if self.is_connected() and self.serial_connection.in_waiting:
            try:
                line = self.serial_connection.readline().decode("utf-8").strip()
                if line:
                    print(f"[SERIAL] Reçu : {line}")
                    self.data_received.emit(line)
            except Exception as e:
                print(f"[Erreur lecture série] {e}")

    def get_last_alcohol_value(self):
        return self.last_validated_alcohol_value

    def close_connection(self):
        try:
            confirmation = QMessageBox.question(
                None, "Confirmation", "Voulez-vous vraiment déconnecter ?",
                QMessageBox.Yes | QMessageBox.No
            )
            if confirmation == QMessageBox.Yes:
                self.read_timer.stop()
                if self.is_connected():
                    self.serial_connection.close()
                self._update_status("Déconnecté", "black")
                self.connection_status_changed.emit(False)
        except Exception as e:
            QMessageBox.warning(None, "Erreur", f"Déconnexion échouée : {e}")

    def set_database_controller(self, db_controller: AlcoolTestController):
        self.db_controller = db_controller
