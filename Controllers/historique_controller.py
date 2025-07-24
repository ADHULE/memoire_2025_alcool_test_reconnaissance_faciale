from Models.database_model import my_session
from Models.historitique_model import HISTORIQUE
from datetime import datetime

class HISTORIQUE_CONTROLLER:
    def __init__(self):
        self.db = my_session

    # Créer un nouvel historique
    def new_history(self, chauffeur_id: int, jour_heure: datetime, event_type: str,
                    person_info: str, alcool_value: float, image_id: int = None) -> HISTORIQUE:
        historique = HISTORIQUE(
            chauffeur_id=chauffeur_id,
            jour_heure=jour_heure,
            event_type=event_type,
            person_info=person_info,
            alcool_value=alcool_value,
            image_id=image_id
        )
        self.db.add(historique)
        self.db.commit()
        self.db.refresh(historique)
        return historique

    # Lire tout
    def get_all_histories(self):
        return self.db.query(HISTORIQUE).order_by(HISTORIQUE.jour_heure.desc()).all()

    # Lire par ID
    def get_by_id(self, historique_id: int) -> HISTORIQUE:
        return self.db.query(HISTORIQUE).filter(HISTORIQUE.id == historique_id).first()

    # Mettre à jour
    def update_history(self, historique_id: int, **kwargs):
        historique = self.get_by_id(historique_id)
        if not historique:
            return None
        for key, value in kwargs.items():
            if hasattr(historique, key):
                setattr(historique, key, value)
        self.db.commit()
        self.db.refresh(historique)
        return historique

    # Supprimer
    def delete_history(self, historique_id: int) -> bool:
        historique = self.get_by_id(historique_id)
        if not historique:
            return False
        self.db.delete(historique)
        self.db.commit()
        return True

    # 🔍 Filtrer par chauffeur
    def get_by_chauffeur(self, chauffeur_id: int):
        return self.db.query(HISTORIQUE).filter(HISTORIQUE.chauffeur_id == chauffeur_id).all()

    # Filtrer par type d'événement
    def get_by_event_type(self, type_str: str):
        return self.db.query(HISTORIQUE).filter(HISTORIQUE.event_type.ilike(f"%{type_str}%")).all()

    # Filtrer par intervalle de date
    def get_by_date_range(self, start: datetime, end: datetime):
        return self.db.query(HISTORIQUE).filter(HISTORIQUE.jour_heure.between(start, end)).all()

    # Filtrer par taux d’alcool
    def get_by_alcool_level(self, min_value: float = 0.5):
        return self.db.query(HISTORIQUE).filter(HISTORIQUE.alcool_value >= min_value).all()

    # Filtrer par image associée
    def get_by_image(self, image_id: int):
        return self.db.query(HISTORIQUE).filter(HISTORIQUE.image_id == image_id).all()
