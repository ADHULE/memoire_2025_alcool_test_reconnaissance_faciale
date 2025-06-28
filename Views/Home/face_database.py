# face_database.py
import cv2


class FaceDatabase:
    def __init__(self, person_controller, image_controller, face_engine, threshold=0.65):
        self.db = []
        self.controller = person_controller
        self.image_controller = image_controller
        self.face_engine = face_engine
        self.threshold = threshold

    def load(self):
        self.db.clear()
        try:
            all_photos = self.image_controller.get_all_photos()
            persons = self.controller.get_driver_by_id(all_photos.personne_id)
        except Exception as e:
            print("Erreur de chargement :", e)
            return

        for chauf in persons:
            try:
                photo = self.image_controller.get_photo(chauf.personne_id)
                if photo:
                    img = cv2.imread(photo.chemin)
                    emb = self.face_engine.encode_face(img)
                    if emb is not None:
                        self.db.append({
                            "nom": f"{chauf.nom} {chauf.prenom}",
                            "embedding": emb
                        })
            except Exception as e:
                print(f"Erreur encodage {chauf.nom}: {e}")

    def identify(self, embedding):
        best_match = {"name": "Inconnu", "score": 0.0}
        for profile in self.db:
            score = self.face_engine.compute_similarity(embedding, profile["embedding"])
            if score > self.threshold and score > best_match["score"]:
                best_match = {"name": profile["nom"], "score": score}
        return best_match
