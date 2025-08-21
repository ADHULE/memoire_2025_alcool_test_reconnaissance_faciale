import os
import sys
import json
import cv2
import numpy as np
from datetime import datetime
from PySide6.QtCore import QObject, Signal, QTimer
from Controllers.alcool_test_controller import AlcoolTestController
from insightface.app import FaceAnalysis
from Controllers.historique_controller import HISTORIQUE_CONTROLLER


def resource_path(relative_path):
    """
    Retourne le chemin absolu d'une ressource, même dans un exécutable PyInstaller.
    """
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class CameraController(QObject):
    """
    Contrôleur principal pour la gestion de la caméra, de la reconnaissance faciale,
    et du suivi des valeurs d'alcool reçues depuis l'Arduino.
    """

    frame_ready = Signal(object)  # Signal : une nouvelle image traitée est prête
    error_occurred = Signal(str)  # Signal : une erreur est survenue
    recognized = Signal(str, float)  # Signal : un visage reconnu avec son score

    def __init__(self, person_controller, image_controller,
                 history_controller=None, arduino_controller=None, parent=None):
        super().__init__(parent)

        # --- Initialisation du moteur de reconnaissance faciale ---
        self.face_engine = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
        self.face_engine.prepare(ctx_id=0)

        # --- Variables caméra ---
        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.process_frame)

        # --- Base de données interne des visages encodés ---
        self.face_db = []
        self.recognition_threshold = 0.65

        # --- Contrôleurs externes ---
        self.person_controller = person_controller
        self.image_controller = image_controller
        self.history_controller = history_controller or HISTORIQUE_CONTROLLER()
        self.arduino_controller = arduino_controller

        # --- Variables détection alcool ---
        self.last_alcool_value = None
        self.last_alcool_timestamp = None
        self.seuil_detection = 0.4

        # Connexion aux données Arduino (si disponible)
        if self.arduino_controller is not None:
            self.arduino_controller.data_received.connect(self.on_data_received)

    # ----------------------------------------------------------------------
    # Gestion des caméras
    # ----------------------------------------------------------------------

    def detect_local_cameras(self):
        available = []
        for index in range(5):
            cap = cv2.VideoCapture(index)
            if cap.read()[0]:
                available.append(f"Caméra {index}")
            cap.release()
        return available

    def start_camera(self, source):
        self.stop_camera()

        if isinstance(source, str) and source.startswith("Caméra"):
            try:
                index = int(source.split(" ")[1])
            except (ValueError, IndexError):
                index = 0
            self.cap = cv2.VideoCapture(index)
        elif isinstance(source, str) and source.startswith(("http://", "https://", "rtsp://")):
            self.cap = cv2.VideoCapture(source)
        elif isinstance(source, int):
            self.cap = cv2.VideoCapture(source)
        else:
            self.error_occurred.emit("Source caméra invalide.")
            return False

        if self.cap.isOpened():
            self.timer.start(30)
            return True
        else:
            self.error_occurred.emit("Impossible d’ouvrir la caméra.")
            return False

    def start_camera_from_url(self, url):
        self.stop_camera()
        if not isinstance(url, str) or not url.startswith(("http://", "https://", "rtsp://")):
            self.error_occurred.emit("URL de caméra invalide.")
            return False

        self.cap = cv2.VideoCapture(url)
        if self.cap.isOpened():
            self.timer.start(30)
            return True
        else:
            self.error_occurred.emit("Impossible d’ouvrir la caméra via l’URL fournie.")
            return False

    def stop_camera(self):
        if self.cap:
            self.timer.stop()
            self.cap.release()
            self.cap = None

    # ----------------------------------------------------------------------
    # Gestion des visages
    # ----------------------------------------------------------------------

    def load_face_database(self):
        self.face_db.clear()
        try:
            images = self.image_controller.get_all_photos()
            if not isinstance(images, (list, tuple)):
                images = [images] if images else []

            for image_obj in images:
                path = resource_path(image_obj.url)

                if not os.path.exists(path):
                    self.error_occurred.emit(f"Fichier introuvable : {path}")
                    continue

                img = cv2.imread(path)
                if img is None:
                    self.error_occurred.emit(f"Impossible de charger l'image : {path}")
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

    def process_frame(self):
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

            for profile in self.face_db:
                sim = np.dot(face.embedding, profile["embedding"]) / (
                        np.linalg.norm(face.embedding) * np.linalg.norm(profile["embedding"]) + 1e-6)
                if sim > self.recognition_threshold and sim > best_score:
                    name = profile["nom"]
                    matched_profile = profile
                    best_score = sim
                    color = (0, 255, 0)

            cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)
            cv2.putText(frame, name, (bbox[0], bbox[1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            if matched_profile:
                self._log_recognition(name, best_score)
                self.recognized.emit(name, best_score)
                self._save_recognition_information(datetime.now(), matched_profile)

        self.frame_ready.emit(frame)

    def _log_recognition(self, name: str, score: float):
        return

    # ----------------------------------------------------------------------
    # Gestion des données Arduino (alcool)
    # ----------------------------------------------------------------------

    def on_data_received(self, line):
        try:
            data = json.loads(line)
            if "alcohol" not in data:
                return

            raw_value = float(data["alcohol"])
            normalized = round(raw_value / 1023.0, 3)
            alert = bool(data.get("alert", False))

            if alert and normalized > self.seuil_detection:
                self.last_alcool_value = normalized
                self.last_alcool_timestamp = datetime.now()

                controller = AlcoolTestController()
                controller.new_alcool_value(self.last_alcool_timestamp, self.last_alcool_value)

        except Exception:
            pass

    def _save_recognition_information(self, date, person_info):
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
