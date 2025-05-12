import serial  # Importation de la bibliothèque pour la communication série
from Views.home.login_page import LOGINWINDOW

class ALCOOL_VALUE:
    SEUIL_ALCOOL = 400  # Seuil défini dans le programme Arduino

    def __init__(self):
        super().__init__()
        self.login = LOGINWINDOW()
        arduino_port_value=self.login._connect_to_arduino
        # Initialisation de la connexion série avec l'Arduino
        self.arduino = serial.Serial(arduino_port_value)  # Assurez-vous d'ajuster le port COM selon votre système

    def lire_donnees(self):
        """Lit la valeur envoyée par l'Arduino et affiche si elle dépasse le seuil."""
        try:
            ligne = self.arduino.readline().decode().strip()  # Lecture et décodage de la ligne reçue depuis l'Arduino

            # Vérification si la ligne contient les données de mesure
            if ligne.startswith("Valeur d'alcool détectée"):
                valeur = int(ligne.split(": ")[1])  # Extraction de la valeur numérique
                print(f"Valeur reçue : {valeur}")

                # Vérification si la valeur dépasse le seuil défini
                if valeur > self.SEUIL_ALCOOL:
                    print("⚠️ Alcool détecté au-dessus du seuil !")
        except Exception as e:
            print(f"Erreur lors de la lecture des données : {str(e)}")  # Gestion des erreurs potentielles

# Création d'une instance de la classe ALCOOL_VALUE
detecteur_alcool = ALCOOL_VALUE()

# Boucle infinie pour surveiller les niveaux d'alcool en temps réel
while True:
    detecteur_alcool.lire_donnees()