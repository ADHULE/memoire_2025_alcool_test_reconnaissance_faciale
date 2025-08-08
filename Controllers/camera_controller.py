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
    frame_ready = Signal(object)
    error_occurred = Signal(str)
    recognized = Signal(str, float)

    def __init__(self, person_controller, image_controller, history_controller=None, arduino_controller=None, parent=None):
        super().__init__(parent)

        self.face_engine = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
        self.face_engine.prepare(ctx_id=0)

        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.process_frame)

        self.face_db = []
        self.recognition_threshold = 0.65

        self.person_controller = person_controller
        self.image_controller = image_controller
        self.history_controller = history_controller or HISTORIQUE_CONTROLLER()
        self.arduino_controller = arduino_controller

        self.last_alcool_value = None
        self.last_alcool_timestamp = None
        self.seuil_detection = 0.4  # Seuil adapté à la valeur normalisée

        if self.arduino_controller is not None:
            self.arduino_controller.data_received.connect(self.on_data_received)

    def detect_local_cameras(self):
        available = []
        for index in range(5):
            cap = cv2.VideoCapture(index)
            if cap.read()[0]:
                available.append(f"Caméra {index}")
            cap.release()
        return available

    def load_face_database(self):
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
            self.error_occurred.emit("Impossible d’ouvrir la caméra.")
            return False

    def stop_camera(self):
        if self.cap:
            self.timer.stop()
            self.cap.release()
            self.cap = None

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
            cv2.putText(frame, name, (bbox[0], bbox[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            if matched_profile:
                self._log_recognition(name, best_score)
                self.recognized.emit(name, best_score)
                self._save_recognition_information(datetime.now(), matched_profile)

        self.frame_ready.emit(frame)

    def _log_recognition(self, name: str, score: float):
        print(f"[RECONNU] {name} avec un score de similarité de {score:.2f}")

    def on_data_received(self, line):
        try:
            print("[DATA REÇUE]", line)
            data = json.loads(line)
            if "alcohol" not in data:
                print("[IGNORÉ] Pas de donnée alcool.")
                return

            raw_value = float(data["alcohol"])
            normalized = round(raw_value / 1023.0, 3)
            alert = bool(data.get("alert", False))

            # print(f"[ALCOOL] brut={raw_value}, normalisé={normalized}, alerte={alert}")

            if alert and normalized > self.seuil_detection:
                self.last_alcool_value = normalized
                self.last_alcool_timestamp = datetime.now()

                controller = AlcoolTestController()
                controller.new_alcool_value(self.last_alcool_timestamp, self.last_alcool_value)
        except Exception as e:
            print("[ERREUR DATA]", e)

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

            # print(f"[VÉRIF] alcool_valide={alcool_valide}, reconnaissance_valide={reconnaissance_valide}")

            if alcool_valide and reconnaissance_valide:
                values_string = f"{nom},{telephone}"
                self.history_controller.new_history(
                    chauffeur_id=chauffeur_id,
                    image_id=image_id,
                    jour_heure=date,
                    person_info=values_string,
                    alcool_value=self.last_alcool_value,
                )

                # print(f"[ENREGISTRÉ] {nom} avec alcool = {self.last_alcool_value}")

                self.last_alcool_value = None
                self.last_alcool_timestamp = None
            else:
               pass
                # print("[IGNORÉ] Conditions non réunies : reconnaissance ou alcool invalide.")

        except Exception as e:
            self.error_occurred.emit(f"Erreur sauvegarde historique : {e}")
            # print("[ERREUR HISTORIQUE]", e)
            if hasattr(self.history_controller, "rollback_session"):
                self.history_controller.rollback_session()
