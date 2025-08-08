import os
import json
import cv2
import numpy as np
from datetime import datetime
from PySide6.QtCore import QObject, Signal, QTimer
from Controllers.alcool_test_controller import AlcoolTestController
from insightface.app import FaceAnalysis
from Controllers.historique_controller import HISTORIQUE_CONTROLLER

class CameraController(QObject):
    # Signaux Qt pour communiquer avec l'interface ou d'autres composants
    frame_ready = Signal(object)              # Signal pour transmettre une image traitée
    error_occurred = Signal(str)              # Signal pour transmettre une erreur ou un message
    recognized = Signal(str, float)           # Signal pour transmettre une reconnaissance faciale réussie

    def __init__(self, person_controller, image_controller, history_controller=None, arduino_controller=None, parent=None):
        super().__init__(parent)

        # Initialisation du moteur de reconnaissance faciale
        self.face_engine = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
        self.face_engine.prepare(ctx_id=0)

        # Initialisation des composants
        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.process_frame)

        self.face_db = []                     # Base de données des visages
        self.recognition_threshold = 0.65     # Seuil de reconnaissance faciale

        self.person_controller = person_controller
        self.image_controller = image_controller
        self.history_controller = history_controller or HISTORIQUE_CONTROLLER()
        self.arduino_controller = arduino_controller

        self.last_alcool_value = None         # Dernière valeur d'alcool reçue
        self.last_alcool_timestamp = None     # Timestamp de la dernière valeur
        self.seuil_detection = 0.4            # Seuil de détection pour la valeur normalisée

        # Connexion au signal de réception des données Arduino
        if self.arduino_controller is not None:
            self.arduino_controller.data_received.connect(self.on_data_received)

    def detect_local_cameras(self):
        # Détection des caméras disponibles localement
        available = []
        for index in range(5):
            cap = cv2.VideoCapture(index)
            if cap.read()[0]:
                available.append(f"Caméra {index}")
            cap.release()
        return available

    def load_face_database(self):
        # Chargement des visages dans la base de données
        self.face_db.clear()
        try:
            images = self.image_controller.get_all_photos()
            if not isinstance(images, (list, tuple)):
                images = [images] if images else []

            for image_obj in images:
                path = image_obj.url
                if not os.path.exists(path):
                    continue

                img = cv2.imread(path)
                if img is None:
                    continue

                person = self.person_controller.get_driver_by_id(image_obj.personne_id)
                faces = self.face_engine.get(img)

                if person and faces:
                    self.face_db.append({
                        "id": person.id,
                        "nom": f"{person.nom} {person.prenom}",
                        "telephone": person.telephone,
                        "embedding": faces[0].embedding,
                        "image_id": image_obj.id,
                    })
        except Exception as e:
            self.error_occurred.emit(f"Erreur chargement visages : {e}")

    def start_camera(self, source):
        # Démarrage de la caméra
        self.stop_camera()
        if isinstance(source, str) and source.startswith("Caméra"):
            try:
                source = int(source.split(" ")[1])
            except (ValueError, IndexError):
                source = 0
        elif not isinstance(source, int):
            source = 0

        self.cap = cv2.VideoCapture(source)
        if self.cap.isOpened():
            self.timer.start(30)
            return True
        else:
            # self.error_occurred.emit("Impossible d’ouvrir la caméra.")
            return False

    def stop_camera(self):
        # Arrêt de la caméra
        if self.cap:
            self.timer.stop()
            self.cap.release()
            self.cap = None

    def process_frame(self):
        # Traitement de chaque trame vidéo
        if not self.cap or not self.cap.isOpened():
            self.stop_camera()
            self.error_occurred.emit("La caméra a été déconnectée ou est indisponible.")
            return

        ret, frame = self.cap.read()
        if not ret:
            self.error_occurred.emit("Impossible de lire une trame de la caméra.")
            return

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        try:
            faces = self.face_engine.get(rgb_frame)
        except Exception as e:
            self.error_occurred.emit(f"Erreur moteur de reconnaissance : {e}")
            return

        for face in faces:
            bbox = face.bbox.astype(int)
            name, best_score, matched_profile = "Inconnu", 0.0, None
            color = (0, 0, 255)

            # Comparaison avec les visages enregistrés
            for profile in self.face_db:
                sim = np.dot(face.embedding, profile["embedding"]) / (
                    np.linalg.norm(face.embedding) * np.linalg.norm(profile["embedding"]) + 1e-6)
                if sim > self.recognition_threshold and sim > best_score:
                    name = profile["nom"]
                    matched_profile = profile
                    best_score = sim
                    color = (0, 255, 0)

            # Affichage du nom sur la trame
            cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)
            cv2.putText(frame, name, (bbox[0], bbox[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            if matched_profile:
                self._log_recognition(name, best_score)
                self.recognized.emit(name, best_score)
                self._save_recognition_information(datetime.now(), matched_profile)

        self.frame_ready.emit(frame)

    def _log_recognition(self, name: str, score: float):
        # Log interne de reconnaissance (désactivé en console)
        # print(f"[RECONNU] {name} avec un score de similarité de {score:.2f}")

        return

    def on_data_received(self, line):
        # Traitement des données reçues de l'Arduino
        try:
            # print("[DATA REÇUE]", line)
            data = json.loads(line)
            if "alcohol" not in data:
                # print("[IGNORÉ] Pas de donnée alcool.")
                return

            raw_value = float(data["alcohol"])
            normalized = round(raw_value / 1023.0, 3)
            alert = bool(data.get("alert", False))

            if alert and normalized > self.seuil_detection:
                self.last_alcool_value = normalized
                self.last_alcool_timestamp = datetime.now()

                controller = AlcoolTestController()
                controller.new_alcool_value(self.last_alcool_timestamp, self.last_alcool_value)


        except Exception as e:
            # self.error_occurred.emit(f"Erreur dans la lecture Arduino : {e}")
            pass

    def _save_recognition_information(self, date, person_info):
        # Sauvegarde des informations de reconnaissance et alcool
        try:
            chauffeur_id = person_info.get("id")
            image_id = person_info.get("image_id")
            nom = person_info.get("nom")
            telephone = person_info.get("telephone")

            alcool_valide = (
                self.last_alcool_value is not None and
                self.last_alcool_timestamp is not None and
                (datetime.now() - self.last_alcool_timestamp).total_seconds() <= 5 and
                self.last_alcool_value > self.seuil_detection
            )

            reconnaissance_valide = chauffeur_id is not None and image_id is not None

            if alcool_valide and reconnaissance_valide:
                values_string = f"{nom},{telephone}"
                self.history_controller.new_history(
                    chauffeur_id=chauffeur_id,
                    image_id=image_id,
                    jour_heure=date,
                    person_info=values_string,
                    alcool_value=self.last_alcool_value,
                )


                self.last_alcool_value = None
                self.last_alcool_timestamp = None

        except Exception as e:
            self.error_occurred.emit(f"Erreur sauvegarde historique : {e}")
            if hasattr(self.history_controller, "rollback_session"):
                self.history_controller.rollback_session()
