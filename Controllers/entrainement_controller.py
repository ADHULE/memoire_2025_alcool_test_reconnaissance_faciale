from sqlalchemy.exc import SQLAlchemyError
from Models.entrainement_image import ENTRAINEMENT
from Models.database_model import my_session


class ENTRAINEMENT_CONTROLLER:

    def new_model(self, model_data, image_id):
        """🔹 Créer un nouvel entraînement"""
        try:
            new_entrainement = ENTRAINEMENT(model_data=model_data, image_id=image_id)

            my_session.add(new_entrainement)
            my_session.commit()
            my_session.refresh(new_entrainement)
            return new_entrainement
        except SQLAlchemyError as e:
            return {"error": f"Échec de la création de l'entraînement : {str(e)}"}

    def get_model(self, entrainement_id):
        """🔹 Récupérer un entraînement par ID"""
        try:

            entrainement = (
                my_session.query(ENTRAINEMENT)
                .filter(ENTRAINEMENT.id == entrainement_id)
                .first()
            )
            if not entrainement:
                return {"error": "Entraînement non trouvé"}
            return entrainement
        except SQLAlchemyError as e:
            return {"error": f"Erreur de récupération : {str(e)}"}

    def update_model(self, entrainement_id, model_data=None, image_id=None):
        """🔹 Mettre à jour un entraînement existant"""
        try:

            entrainement = (
                my_session.query(ENTRAINEMENT)
                .filter(ENTRAINEMENT.id == entrainement_id)
                .first()
            )
            if not entrainement:
                return {"error": "Entraînement non trouvé"}

            if model_data:
                entrainement.model_data = model_data
            if image_id:
                entrainement.image_id = image_id

            my_session.commit()
            my_session.refresh(entrainement)
            return entrainement
        except SQLAlchemyError as e:
            return {"error": f"Erreur lors de la mise à jour : {str(e)}"}

    def delete_model(self, entrainement_id):
        """🔹 Supprimer un entraînement par ID"""
        try:

            entrainement = (
                my_session.query(ENTRAINEMENT)
                .filter(ENTRAINEMENT.id == entrainement_id)
                .first()
            )
            if not entrainement:
                return {"error": "Entraînement non trouvé"}

            my_session.delete(entrainement)
            my_session.commit()
            return {"message": "Entraînement supprimé avec succès"}
        except SQLAlchemyError as e:
            return {"error": f"Erreur lors de la suppression : {str(e)}"}
