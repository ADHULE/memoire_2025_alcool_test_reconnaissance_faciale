import logging
from sqlalchemy.exc import SQLAlchemyError
from Models.database_model import my_session
from Models.historitique_model import HISTORIQUE  # Assure-toi que le nom du fichier est bien "historique_model.py"

class HISTORIQUE_CONTROLLER:
    """Contrôleur pour gérer les opérations CRUD sur les historiques."""

    def new_history(self, jour_heure, chauffeur_id, event_type, person_info, alcool_value):
        """Ajoute un nouvel événement historique dans la base de données."""
        try:
            new = HISTORIQUE(
                jour_heure=jour_heure,
                chauffeur_id=chauffeur_id,
                event_type=event_type,
                person_info=person_info,
                alcool_value=alcool_value
            )
            my_session.add(new)
            my_session.commit()
            my_session.refresh(new)
            return new
        except SQLAlchemyError as e:
            my_session.rollback()
            logging.error(f"Erreur lors de l'enregistrement de l'historique : {str(e)}", exc_info=True)
            return None

    def get_histories(self):
        """Retourne tous les enregistrements historiques."""
        try:
            return my_session.query(HISTORIQUE).all()
        except SQLAlchemyError as e:
            logging.error(f"Erreur de chargement des historiques : {str(e)}", exc_info=True)
            return []

    def get_history(self, history_id):
        """Récupère un historique par son identifiant unique."""
        try:
            return my_session.query(HISTORIQUE).filter_by(id=history_id).first()
        except SQLAlchemyError as e:
            logging.error(f"Erreur de récupération de l'historique : {str(e)}", exc_info=True)
            return None

    def update_history(self, history_id, **kwargs):
        """Met à jour dynamiquement les champs d’un historique existant."""
        try:
            history = self.get_history(history_id)
            if not history:
                logging.warning(f"Aucun historique trouvé avec l'ID {history_id}")
                return None

            valid_fields = {"jour_heure", "chauffeur_id", "event_type", "person_info", "alcool_value"}
            for key, value in kwargs.items():
                if key in valid_fields:
                    setattr(history, key, value)

            my_session.commit()
            my_session.refresh(history)
            return history
        except SQLAlchemyError as e:
            my_session.rollback()
            logging.error(f"Erreur de mise à jour de l'historique : {str(e)}", exc_info=True)
            return None

    def delete_history(self, history_id):
        """Supprime un historique par son identifiant."""
        try:
            history = self.get_history(history_id)
            if history:
                my_session.delete(history)
                my_session.commit()
                return True
            logging.warning(f"Aucun historique à supprimer avec l'ID {history_id}")
            return False
        except SQLAlchemyError as e:
            my_session.rollback()
            logging.error(f"Erreur lors de la suppression de l'historique : {str(e)}", exc_info=True)
            return False

    def filter_history(self, start_date=None, end_date=None, event_type=None):
        """Filtre les historiques selon la date et/ou le type d’événement."""
        try:
            query = my_session.query(HISTORIQUE)
            if start_date:
                query = query.filter(HISTORIQUE.jour_heure >= start_date)
            if end_date:
                query = query.filter(HISTORIQUE.jour_heure <= end_date)
            if event_type:
                query = query.filter(HISTORIQUE.event_type == event_type)
            return query.all()
        except SQLAlchemyError as e:
            logging.error(f"Erreur lors du filtrage de l'historique : {str(e)}", exc_info=True)
            return []
