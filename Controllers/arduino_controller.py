import serial
import serial.tools.list_ports
import json
from PySide6.QtCore import QObject, QThread, Signal, Slot
from PySide6.QtWidgets import QMessageBox
from Controllers.alcool_test_controller import AlcoolTestController

class ArduinoController(QObject):
    # Signal émis lorsqu'une ligne de donnée est reçue
    data_received = Signal(str)
    # Signal émis lorsque le statut de la connexion change
    connection_status_changed = Signal(bool)

    def __init__(self, port_combobox=None, status_label=None, seuil_ivresse=0.4):
        """
        Initialise le contrôleur Arduino.
        - port_combobox : menu déroulant pour sélectionner un port série
        - status_label : widget d'affichage du statut de connexion
        - seuil_ivresse : seuil au-delà duquel on considère que la personne est alcoolisée
        """
        super().__init__()
        self.port_combobox = port_combobox
        self.status_label = status_label
        self.seuil_ivresse = seuil_ivresse
        self.serial_connection = None  # Connexion série avec Arduino
        self.last_alcohol_value = None  # Dernière valeur brute reçue
        self.last_validated_alcohol_value = None  # Dernière valeur au-dessus du seuil
        self.reader_thread = QThread()  # Thread pour lire en continu
        self.reading = False
        self.moveToThread(self.reader_thread)
        self.reader_thread.started.connect(self._read_loop)

    def detect_serial_ports(self):
        """
        Détecte les ports série disponibles et les affiche dans le menu déroulant.
        """
        if self.port_combobox:
            self.port_combobox.clear()
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if self.port_combobox:
                self.port_combobox.addItem(f"{port.device} - {port.description}")
        if not ports and self.port_combobox:
            self.port_combobox.addItem("Aucun port série détecté")

    def connect_to_arduino(self):
        """
        Établit une connexion série avec le port sélectionné par l'utilisateur.
        """
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
        """
        Met à jour le statut visuel de la connexion.
        """
        if self.status_label:
            self.status_label.setText(text)
            self.status_label.setStyleSheet(f"color: {color}; font-weight: bold;")

    def is_connected(self):
        """
         Vérifie si la connexion série est active.
        """
        return self.serial_connection and self.serial_connection.is_open

    def start_reading(self):
        """
        Lance le thread de lecture en continu.
        """
        if not self.reader_thread.isRunning():
            self.reading = True
            self.reader_thread.start()

    @Slot()
    def _read_loop(self):
        """Boucle de lecture active tant que la connexion est ouverte. Lit les lignes envoyées par Arduino.
        """
        while self.reading and self.is_connected():
            try:
                if self.serial_connection.in_waiting:
                    line = self.serial_connection.readline().decode("utf-8").strip()
                    if line:
                        print(f"[SERIAL] Reçu : {line}")
                        self.extract_alcohol_value(line)
                        self.data_received.emit(line)
            except Exception as e:
                print(f"[Erreur lecture série] {e}")

    def extract_alcohol_value(self, raw_line: str):
        """ Extrait et normalise la valeur d'alcool depuis une ligne JSON.
        Met à jour la dernière valeur valide uniquement si elle dépasse le seuil.
        """
        try:
            data = json.loads(raw_line)
            if "alcohol" in data:
                raw_value = float(data["alcohol"])
                normalized = round(raw_value / 1023.0, 3)
                self.last_alcohol_value = normalized

                if normalized >= self.seuil_ivresse:
                    self.last_validated_alcohol_value = normalized
                    # Enregistrement en BDD possible ici (commenté)
                    # if hasattr(self, "db_controller"):
                    #     self.db_controller.new_alcool_value(datetime.now(), normalized)
                else:
                    self.last_validated_alcohol_value = None
        except (json.JSONDecodeError, ValueError) as e:
            print(f"[ERROR] Erreur de parsing JSON : {e}")

    def get_last_alcohol_value(self):
        #Retourne la dernière valeur validée (>= seuil).
        return self.last_validated_alcohol_value

    def stop_reading(self):
        #Arrête la lecture du port série et le thread associé.
        self.reading = False
        if self.reader_thread.isRunning():
            self.reader_thread.quit()
            self.reader_thread.wait()

    def close_connection(self):
        #Ferme proprement la connexion série après confirmation utilisateur.
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

    def set_database_controller(self, db_controller: AlcoolTestController):
        # Injecte une instance du contrôleur de base de données pour enregistrement.
        self.db_controller = db_controller
