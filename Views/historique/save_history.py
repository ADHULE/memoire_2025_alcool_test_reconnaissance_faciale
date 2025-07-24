import datetime
from Controllers.historique_controller import HISTORIQUE_CONTROLLER
from Controllers.arduino_controller import ArduinoController
from Controllers.camera_controller import CameraController


class Save_Historique:

    def __init__(self, camera_controller: CameraController, arduino_controller: ArduinoController):
        self.camera_controller = camera_controller
        self.arduino_controller = arduino_controller
        self.historique_controller = HISTORIQUE_CONTROLLER()

    def extract_data_for_historique(self):
        # Récupère les données nécessaires à l'enregistrement depuis les contrôleurs.

        recognition = self.camera_controller.get_last_recognition()
        if not recognition:
            return None  # Aucun visage reconnu

        name, chauffeur_id, score = recognition
        alcool_value = self.arduino_controller.last_alcohol_value
        event_type = self._determiner_event_type(alcool_value)

        if chauffeur_id is None or alcool_value is None:
            return None  # Données incomplètes

        return {
            "name": name,
            "chauffeur_id": chauffeur_id,
            "event_type": event_type,
            "alcool_value": alcool_value
        }

    def save_to_database(self):

        data = self.extract_data_for_historique()
        if not data:
            return False

        try:
            historique = self.historique_controller.new_history(
                jour_heure=datetime.datetime.now(),
                chauffeur_id=data["chauffeur_id"],
                event_type=data["event_type"],
                person_info=data["name"],
                alcool_value=data["alcool_value"]
            )
            return historique is not None
        except Exception:
            return False

    def _determiner_event_type(self, taux: float, seuil=0.5) -> str:

        #Détermine le type d'événement selon le taux d'alcool.

        if taux is None:
            return "reconnaissance simple (taux inconnu)"
        return "reconnaissance + alerte alcool" if taux >= seuil else "reconnaissance simple"
