import datetime
import os
import cv2
import numpy as np
from PySide6.QtCore import QObject, Signal, QTimer
from insightface.app import FaceAnalysis
from PySide6.QtWidgets import QMessageBox

from Controllers.historique_controller import HISTORIQUE_CONTROLLER


class CameraController(QObject):
    frame_ready = Signal(object)
    error_occurred = Signal(str)
    recognized = Signal(str, float)

    def __init__(self, person_controller, image_controller, arduino_controller, parent=None):
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
        self.arduino_controller = arduino_controller

    def detect_local_cameras(self):
        available = []
        for index in range(5):
            cap = cv2.VideoCapture(index)
            if cap.read()[0]:
                available.append(f"Caméra {index}")
                cap.release()
        return available if available else ["Aucune caméra détectée"]

    def load_face_database(self):
        self.face_db.clear()
        try:
            images = self.image_controller.get_all_photos()
            if not isinstance(images, (list, tuple)):
                images = [images] if images else []

            for image_obj in images:
                path = image_obj.url
                if not os.path.exists(path):
                    print(f"Avertissement: L'image {path} n'existe pas.")
                    continue
                img = cv2.imread(path)
                if img is None:
                    print(f"Avertissement: Impossible de lire l'image {path}.")
                    continue

                person = self.person_controller.get_driver_by_id(image_obj.personne_id)
                faces = self.face_engine.get(img)
                if person and faces:
                    self.face_db.append({
                        "id": person.id,
                        "nom": f"{person.nom} {person.prenom}",
                        "telephone": person.telephone,
                        "embedding": faces[0].embedding
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
        self.cap = cv2.VideoCapture(source)
        if self.cap.isOpened():
            self.timer.start(30)
            return True
        else:
            self.error_occurred.emit(f"Erreur d’accès caméra ou source invalide: {source}")
            return False

    def stop_camera(self):
        self.timer.stop()
        if self.cap:
            self.cap.release()
        self.cap = None

    def determiner_event_type(self, taux: float, seuil=0.5):
        if taux is None:
            return "reconnaissance simple (taux inconnu)"
        return "reconnaissance + alerte alcool" if taux >= seuil else "reconnaissance simple"

    def process_frame(self):
        if not self.cap or not self.cap.isOpened():
            return

        ret, frame = self.cap.read()
        if not ret:
            return

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        faces = self.face_engine.get(rgb_frame)

        for face in faces:
            bbox = face.bbox.astype(int)
            name, best_score, matched_id = "Inconnu", 0.0, None
            color = (0, 0, 255)

            for profile in self.face_db:
                sim = np.dot(face.embedding, profile["embedding"]) / (
                    np.linalg.norm(face.embedding) * np.linalg.norm(profile["embedding"]) + 1e-6)
                if sim > self.recognition_threshold and sim > best_score:
                    name = profile["nom"]
                    matched_id = profile["id"]
                    best_score = sim
                    color = (0, 255, 0)

            cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)
            cv2.putText(frame, name, (bbox[0], bbox[1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            if name != "Inconnu":
                alcool_value = getattr(self.arduino_controller, 'last_alcohol_value', None)
                event_type = self.determiner_event_type(alcool_value)
                self._log_recognition(name, best_score)
                self._save_to_database(name, matched_id, event_type, alcool_value)
                self.recognized.emit(name, best_score)

        self.frame_ready.emit(frame)

    def _log_recognition(self, name: str, score: float):
        print(f"Reconnu: {name} (Score: {score:.2f})")

    def _save_to_database(self, name: str, chauffeur_id: int, event_type: str, alcool_value: float):
        print(
            f"[DEBUG] Tentative d'enregistrement - Nom: {name}, ID: {chauffeur_id}, Alcool: {alcool_value}, Type: {event_type}")

        if chauffeur_id is not None and alcool_value is not None:
            try:
                timestamp = datetime.datetime.now()
                historique_ctrl = HISTORIQUE_CONTROLLER()

                result = historique_ctrl.new_history(
                    jour_heure=timestamp,
                    chauffeur_id=chauffeur_id,
                    event_type=event_type,
                    person_info=name,
                    alcool_value=alcool_value
                )

                if result:
                    # print("[INFO]  Enregistrement réussi dans la base de données.")
                    QMessageBox.information(None, "Succès", f"Historique enregistré pour {name} à {timestamp}")
                else:
                    # print("[WARNING] Enregistrement non confirmé : la méthode new_history n’a rien retourné.")
                    QMessageBox.warning(None, "Attention", "Échec possible de l'enregistrement.")
            except Exception as e:
                # print(f"[ERROR] Erreur lors de l'insertion : {e}")
                QMessageBox.critical(None, "Erreur", f"Insertion impossible : {e}")
                self.error_occurred.emit(f"Erreur insertion historique : {e}")
        else:
            # print("[INFO] Conditions d'enregistrement non remplies (chauffeur ou alcool manquant)")
            QMessageBox.information(None, "Information",
                                    "Visage reconnu ou alcool non détecté — enregistrement ignoré.")
