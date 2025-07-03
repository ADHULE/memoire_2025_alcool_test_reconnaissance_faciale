import serial
import serial.tools.list_ports
from PySide6.QtCore import QObject, QThread, Signal, Slot

class ArduinoController(QObject):
    data_received = Signal(str)
    connection_status_changed = Signal(bool)

    def __init__(self, port_combobox=None, status_label=None):
        super().__init__()
        self.port_combobox = port_combobox
        self.status_label = status_label
        self.serial_connection = None
        self.reader_thread = QThread()
        self.reading = False
        self.moveToThread(self.reader_thread)
        self.reader_thread.started.connect(self._read_loop)

    def detect_serial_ports(self):
        if self.port_combobox:
            self.port_combobox.clear()
        ports = serial.tools.list_ports.comports()
        if not ports and self.port_combobox:
            self.port_combobox.addItem("Aucun port série détecté")
        else:
            for port in ports:
                if self.port_combobox:
                    self.port_combobox.addItem(f"{port.device} - {port.description}")

    def connect_to_arduino(self):
        if not self.port_combobox:
            self._emit_connection_status(False)
            return

        selected = self.port_combobox.currentText()
        if " - " not in selected:
            self._update_status("🔴 Aucun port valide sélectionné", "red")
            self._emit_connection_status(False)
            return

        port = selected.split(" - ")[0]
        try:
            self.serial_connection = serial.Serial(port, baudrate=9600, timeout=1)
            self._update_status(f"🟢 Connecté à {port}", "green")
            if self.port_combobox:
                self.port_combobox.clear()
                self.port_combobox.addItem(port)
            self.start_reading()
            self._emit_connection_status(True)
        except serial.SerialException:
            self._update_status(f"🔴 Erreur de connexion à {port}", "red")
            self._emit_connection_status(False)

    def _emit_connection_status(self, connected: bool):
        self.connection_status_changed.emit(connected)

    def _update_status(self, text, color):
        if self.status_label:
            self.status_label.setText(text)
            self.status_label.setStyleSheet(f"color: {color}; font-weight: bold")

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
                        self.data_received.emit(line)
            except Exception as e:
                print(f"[Erreur de lecture] {e}")

    def stop_reading(self):
        self.reading = False
        if self.reader_thread.isRunning():
            self.reader_thread.quit()
            self.reader_thread.wait()

    def send_command(self, cmd: str):
        if self.is_connected():
            try:
                self.serial_connection.write(cmd.encode())
            except Exception as e:
                print(f"[Erreur d'envoi] {e}")

    def close_connection(self):
        self.stop_reading()
        if self.is_connected():
            self.serial_connection.close()
        self._update_status("Statut : Déconnecté", "black")
        self._emit_connection_status(False)
