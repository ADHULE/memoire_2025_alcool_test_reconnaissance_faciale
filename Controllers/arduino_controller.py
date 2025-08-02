import serial
import serial.tools.list_ports
import json
from PySide6.QtCore import QObject, QThread, Signal, Slot
from PySide6.QtWidgets import QMessageBox
from  Controllers.alcool_test_controller import AlcoolTestController
from datetime import datetime
class ArduinoController(QObject):

    data_received = Signal(str)
    connection_status_changed = Signal(bool)

    def __init__(self, port_combobox=None, status_label=None):
        super().__init__()
        self.port_combobox = port_combobox
        self.status_label = status_label
        self.serial_connection = None
        self.last_alcohol_value = None  # Stocke le dernier taux d'alcool (float)
        self.reader_thread = QThread()
        self.reading = False
        self.moveToThread(self.reader_thread)
        self.reader_thread.started.connect(self._read_loop)

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
            self._update_status("🔴 Aucun port valide sélectionné", "red")
            self.connection_status_changed.emit(False)
            return

        port = selected.split(" - ")[0]
        try:
            self.serial_connection = serial.Serial(port, 9600, timeout=1)
            self._update_status(f"🟢 Connecté à {port}", "green")
            self.port_combobox.clear()
            self.port_combobox.addItem(port)
            self.start_reading()
            self.connection_status_changed.emit(True)
        except serial.SerialException:
            self._update_status("🔴 Erreur de connexion", "red")
            self.connection_status_changed.emit(False)

    def _update_status(self, text, color):
        if self.status_label:
            self.status_label.setText(text)
            self.status_label.setStyleSheet(f"color: {color}; font-weight: bold;")

    def is_connected(self):
        return self.serial_connection and self.serial_connection.is_open

    def start_reading(self):
        if not self.reader_thread.isRunning():
            self.reading = True
            self.reader_thread.start()

    @Slot()
    def _read_loop(self):
        while self.reading and self.is_connected():
            try:
                if self.serial_connection.in_waiting:
                    line = self.serial_connection.readline().decode("utf-8").strip()
                    if line:
                        print(f"[SERIAL] Reçu : {line}")  # Journalisation brute
                        self.extract_alcohol_value(line)
                        self.data_received.emit(line)
            except Exception as e:
                print(f"[Erreur lecture série] {e}")
    #
    # def extract_alcohol_value(self, raw_line: str):
    #     try:
    #         data = json.loads(raw_line)
    #         if "alcohol" in data:
    #             raw_value = float(data["alcohol"])
    #             normalized = round(raw_value / 1023.0, 3)
    #             self.last_alcohol_value = normalized
    #             print(f"[INFO] Valeur d'alcool extraite : {self.last_alcohol_value}")
    #         else:
    #             print("[WARNING] Clé 'alcohol' absente.")
    #     except (json.JSONDecodeError, ValueError) as e:
    #         print(f"[ERROR] Erreur de parsing JSON : {e}")

    def set_database_controller(self, db_controller: AlcoolTestController):
        self.db_controller = db_controller

    def extract_alcohol_value(self, raw_line: str):
        try:
            data = json.loads(raw_line)
            if "alcohol" in data:
                raw_value = float(data["alcohol"])
                normalized = round(raw_value / 1023.0, 3)
                self.last_alcohol_value = normalized
                print(f"[INFO] Valeur d'alcool extraite : {self.last_alcohol_value}")

                if hasattr(self, "db_controller"):
                    self.db_controller.new_alcool_value(datetime.now(), normalized)
            else:
                print("[WARNING] Clé 'alcohol' absente.")
        except (json.JSONDecodeError, ValueError) as e:
            print(f"[ERROR] Erreur de parsing JSON : {e}")

    def stop_reading(self):
        self.reading = False
        if self.reader_thread.isRunning():
            self.reader_thread.quit()
            self.reader_thread.wait()

    # def send_command(self, cmd: str):
    #     if self.is_connected():
    #         try:
    #             self.serial_connection.write((cmd + "\n").encode())
    #         except Exception as e:
    #             print(f"[Erreur d'envoi] {e}")

    def close_connection(self):
        try:
            confirmation = QMessageBox.question(
                None, "Confirmation", "Voulez-vous vraiment déconnecter ?",
                QMessageBox.Yes | QMessageBox.No
            )
            if confirmation == QMessageBox.Yes:
                self.stop_reading()
                if self.is_connected():
                    self.serial_connection.close()
                self._update_status("Déconnecté", "black")
                self.connection_status_changed.emit(False)
        except Exception as e:
            QMessageBox.warning(None, "Erreur", f"Déconnexion échouée : {e}")
