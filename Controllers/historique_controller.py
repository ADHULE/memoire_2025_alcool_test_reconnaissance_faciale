from datetime import datetime

from Models.database_model import my_session
from Models.historitique_model import HISTORIQUE
from Models.chauffeur_model import CHAUFFEUR


class HISTORIQUE_CONTROLLER:
    def __init__(self):
        self.db = my_session

    # Créer un nouvel historique
    def new_history(self, chauffeur_id, image_id, jour_heure, person_info, alcool_value=None):
        historique = HISTORIQUE(
            chauffeur_id=chauffeur_id,
            image_id=image_id,
            jour_heure=jour_heure,
            person_info=person_info,
            alcool_value=alcool_value
        )
        self.db.add(historique)
        self.db.commit()
        self.db.refresh(historique)

    # Lire tout
    def get_all_histories(self):
        return self.db.query(HISTORIQUE).order_by(HISTORIQUE.jour_heure.desc()).all()

    # Lire par ID
    def get_by_id(self, historique_id: int) -> HISTORIQUE:
        return self.db.query(HISTORIQUE).filter(HISTORIQUE.id == historique_id).first()


    # Supprimer
    def delete_history(self, historique_id: int) -> bool:
        historique = self.get_by_id(historique_id)
        if not historique:
            return False
        self.db.delete(historique)
        self.db.commit()
        return True

    # Filtrer par chauffeur
    def get_by_chauffeur(self, chauffeur_id: int):
        return self.db.query(HISTORIQUE).filter(HISTORIQUE.chauffeur_id == chauffeur_id).all()


    # Filtrer par intervalle de date
    def get_by_date_range(self, start: datetime, end: datetime):
        return self.db.query(HISTORIQUE).filter(HISTORIQUE.jour_heure.between(start, end)).all()

    # Filtrer par taux d’alcool
    def get_by_alcool_level(self, min_value: float = 0.5):
        return self.db.query(HISTORIQUE).filter(HISTORIQUE.alcool_value >= min_value).all()

    # Récupérer le chemin de l'image du chauffeur à partir de son identifiant
    def get_chauffeur_image_path(self, chauffeur_id: int) -> str:
        chauffeur = self.db.query(CHAUFFEUR).filter(CHAUFFEUR.id == chauffeur_id).first()
        if chauffeur and hasattr(chauffeur, "photo_path"):
            return chauffeur.photo_path
        return ""

