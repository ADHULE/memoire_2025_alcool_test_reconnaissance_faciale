import os
from datetime import datetime
import cv2
import numpy as np
from PySide6.QtCore import QObject, Signal, QTimer
from insightface.app import FaceAnalysis

class CameraController(QObject):
    #Signaux pour l’interface graphique
    frame_ready = Signal(object)
    error_occurred = Signal(str)
    recognized = Signal(str, float)

    def __init__(self, person_controller, image_controller, history_controller=None, arduino_controller=None, parent=None):
        super().__init__(parent)

        #Initialisation du moteur de reconnaissance faciale
        self.face_engine = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
        self.face_engine.prepare(ctx_id=0)

        #Variables de capture
        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.process_frame)

        #Base de données des visages connus
        self.face_db = []
        self.recognition_threshold = 0.65

        #Contrôleurs externes
        self.person_controller = person_controller
        self.image_controller = image_controller
        self.history_controller = history_controller
        self.arduino_controller = arduino_controller

    def detect_local_cameras(self):
        #Détecte les caméras disponibles localement
        available = []
        for index in range(5):
            cap = cv2.VideoCapture(index)
            if cap.read()[0]:
                available.append(f"Caméra {index}")
            cap.release()
        return available

    def load_face_database(self):
        # Charge la base des visages depuis les photos enregistrées
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
        # Lance la capture à partir de la source spécifiée
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
        return False

    def stop_camera(self):
        #Arrête proprement la caméra et libère les ressources
        if self.cap:
            self.timer.stop()
            self.cap.release()
            self.cap = None

    def process_frame(self):
        # Traite chaque trame capturée de la caméra
        if not self.cap or not self.cap.isOpened():
            self.stop_camera()
            self.error_occurred.emit("La caméra a été déconnectée ou est indisponible.")
            return

        ret, frame = self.cap.read()
        if not ret:
            self.error_occurred.emit("Impossible de lire une trame de la caméra.")
            return

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        faces = self.face_engine.get(rgb_frame)

        for face in faces:
            bbox = face.bbox.astype(int)
            name, best_score, matched_profile = "Inconnu", 0.0, None
            color = (0, 0, 255)

            for profile in self.face_db:
                # Calcul de la similarité avec les visages connus
                sim = np.dot(face.embedding, profile["embedding"]) / (
                    np.linalg.norm(face.embedding) * np.linalg.norm(profile["embedding"]) + 1e-6)
                if sim > self.recognition_threshold and sim > best_score:
                    name = profile["nom"]
                    matched_profile = profile
                    best_score = sim
                    color = (0, 255, 0)

            #  Affichage visuel du résultat
            cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)
            cv2.putText(frame, name, (bbox[0], bbox[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            if matched_profile:
                self._log_recognition(name, best_score)
                self.recognized.emit(name, best_score)

                self._save_recognition_information(
                    date=datetime.now(),
                    person_info=matched_profile,
                )

        # Émet la trame mise à jour vers l’interface
        self.frame_ready.emit(frame)

    def _log_recognition(self, name: str, score: float):
        # Journalisation simple des reconnaissances
        return # Peut être remplacé par un logger structuré si nécessaire

    def _save_recognition_information(self, date, person_info):
        # Sauvegarde dans l'historique si visage reconnu ET alcool détecté
        try:
            chauffeur_id = person_info.get("id")
            image_id = person_info.get("image_id")
            nom = person_info.get("nom")
            telephone = person_info.get("telephone")
            alcool_value = self.arduino_controller.get_last_alcohol_value() if self.arduino_controller else None

            #  Enregistrement uniquement si les deux conditions sont réunies
            if chauffeur_id and alcool_value is not None:

                values_string = f"{nom},{telephone}"
                self.history_controller.new_history(
                    chauffeur_id=chauffeur_id,
                    image_id=image_id,
                    jour_heure=date,
                    person_info=values_string,
                    alcool_value=alcool_value,
                )
        except Exception as e:
            # Annulation si échec de sauvegarde
            if hasattr(self.history_controller, "rollback_session"):
                self.history_controller.rollback_session()
