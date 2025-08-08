import json
from PySide6.QtWidgets import QMainWindow, QLabel, QTextEdit, QVBoxLayout, QWidget
from Controllers.alcool_test_controller import AlcoolTestController

class Mq3ValueGui(QMainWindow):
    def __init__(self, arduino_controller):
        super().__init__()
        self.setWindowTitle("LECTURE DE LA VALEUR DE CAPTEUR D'ALCOOL")
        self.arduino_controller = arduino_controller

        # Création du widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Label de statut de connexion
        self.status_label = QLabel("Microcontrôleur : Déconnecté")
        self.status_label.setStyleSheet("font-weight: bold; color: red;")

        # Zone d'affichage des mesures
        self.output_display = QTextEdit()
        self.output_display.setReadOnly(True)

        self.save_alcool_value = None

        # Mise en page verticale
        layout = QVBoxLayout()
        layout.addWidget(self.status_label)
        layout.addWidget(QLabel("Mesures en temps réel :"))
        layout.addWidget(self.output_display)
        central_widget.setLayout(layout)

        # Connexion des signaux du contrôleur Arduino
        self.arduino_controller.data_received.connect(self.on_data_received)
        self.arduino_controller.connection_status_changed.connect(self.update_status_label)

        # Contrôleur de base de données pour enregistrer les valeurs
        self.database_controller = AlcoolTestController()
        self.arduino_controller.set_database_controller(self.database_controller)

    def update_status_label(self, connected):
        # Mise à jour du label de statut selon la connexion
        if connected:
            self.status_label.setText("Microcontrôleur : Connecté")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.status_label.setText("Microcontrôleur :  Déconnecté")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")

    def on_data_received(self, line):
        # Traitement des données reçues du capteur
        try:
            data = json.loads(line)

            if "alcohol" not in data:
                raise ValueError("Donnée 'alcohol' manquante.")

            raw_value = float(data["alcohol"])
            normalized = round(raw_value / 1023.0, 3)
            alert = bool(data.get("alert", False))
            seuil_detection = 400

            # Choix de la couleur selon l'alerte
            couleur = "red" if alert else "green"
            msg_html = f"<span style='color:{couleur};'>{normalized} mg/L</span>"

            # Sauvegarde si la valeur dépasse le seuil
            if alert and raw_value > seuil_detection:
                self.save_alcool_value = raw_value
            elif normalized > 0:
                # print(f"[INFO] Valeur normalisée enregistrée : {normalized}")
                pass

        except (json.JSONDecodeError, ValueError) as e:
            # Affichage d'une erreur dans la zone de texte
            msg_html = f"<span style='color:orange;'>[Erreur] Ligne non valide : {line} ({e})</span>"

        # Ajout du message dans l'affichage
        self.output_display.append(msg_html)

    def _save_alcool_value(self):
        # Retourne la dernière valeur d'alcool enregistrée
        return self.save_alcool_value
