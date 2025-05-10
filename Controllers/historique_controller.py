from Models.database_model import my_session
from Models.historitique_model import HISTORIQUE

import logging


class HISTORIQUE_CONTROLLER:

    def new_history(self, jour_heure, event_type):
        """Ajoute un nouvel événement historique."""
        try:
            new = HISTORIQUE(jour_heure=jour_heure, event_type=event_type)
            my_session.add(new)
            my_session.commit()
            my_session.refresh(new)
            return new
        except Exception as e:
            logging.error(
                f"Erreur lors de l'enregistrement de l'historique : {str(e)}")

    def get_histories(self):
        try:
            return my_session.query(HISTORIQUE).all()
        except Exception as e:
            logging.error(f"Erreur de chargement des historiques: {e}")
            return None

    def get_history(self, history_id):
        """Récupère un événement historique par son ID."""
        try:
            return my_session.query(HISTORIQUE).filter_by(id=history_id).first()
        except Exception as e:
            logging.error(
                f"Erreur lors de la récupération de l'historique : {str(e)}")

    def update_history(self, history_id, jour_heure=None, event_type=None):
        """Met à jour un événement historique."""
        try:
            history = my_session.query(
                HISTORIQUE).filter_by(id=history_id).first()
            if history:
                if jour_heure:
                    history.jour_heure = jour_heure
                if event_type:
                    history.event_type = event_type
                my_session.commit()
                return history
        except Exception as e:
            logging.error(
                f"Erreur lors de la mise à jour de l'historique : {str(e)}")

    def delete_history(self, history_id):
        """Supprime un événement historique."""
        try:
            history = my_session.query(
                HISTORIQUE).filter_by(id=history_id).first()
            if history:
                my_session.delete(history)
                my_session.commit()
        except Exception as e:
            logging.error(
                f"Erreur lors de la suppression de l'historique : {str(e)}")

    def filter_history(self, start_date=None, end_date=None, event_type=None):
        """Filtre les événements historiques selon les critères fournis."""
        try:
            query = my_session.query(HISTORIQUE)
            if start_date:
                query = query.filter(HISTORIQUE.jour_heure >= start_date)
            if end_date:
                query = query.filter(HISTORIQUE.jour_heure <= end_date)
            if event_type:
                query = query.filter(HISTORIQUE.event_type == event_type)
            return query.all()
        except Exception as e:
            logging.error(
                f"Erreur lors du filtrage de l'historique : {str(e)}")
