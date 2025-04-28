from Models.database_model import my_session
from sqlalchemy.exc import SQLAlchemyError
import logging
from Models.chauffeur_model import CHAUFFEUR  
from Models.image_model import IMAGE

logging.basicConfig(level=logging.INFO)

class CHAUFFEUR_CONTROLLER:
    """
    Contrôleur pour gérer les opérations CRUD sur les objets Chauffeur.
    """

    def new_driver(self, nom, postnom, prenom, telephone, email, numero_permis):
        """
        Crée un nouveau chauffeur et l'enregistre en base de données.
        """
        try:
            new_driver = CHAUFFEUR(
                nom=nom,
                postnom=postnom,
                prenom=prenom,
                telephone=telephone,
                email=email,
                numero_permis=numero_permis,
            )
            with my_session.begin():
                my_session.add(new_driver)
                my_session.refresh(new_driver)
            return new_driver
        except SQLAlchemyError as e:
            logging.error("Erreur lors de la création du chauffeur: %s", e)
            raise e

    def get_driver(self, driver_id):
        """
        Récupère un chauffeur par son identifiant.
        """
        try:
            driver = my_session.get(CHAUFFEUR, driver_id)
            if driver is None:
                logging.warning("Aucun chauffeur trouvé avec l'id: %s", driver_id)
            return driver
        except SQLAlchemyError as e:
            logging.error("Erreur lors de la récupération du chauffeur (id=%s): %s", driver_id, e)
            raise e

    def get_all_drivers(self):
        """
        Récupère tous les chauffeurs présents en base de données.
        """
        try:
            return my_session.query(CHAUFFEUR).all()
        except SQLAlchemyError as e:
            logging.error("Erreur lors de la récupération de tous les chauffeurs: %s", e)
            raise e

    def update_driver(self, driver_id, **kwargs):
        """
        Met à jour les attributs d'un chauffeur existant.
        """
        try:
            driver = my_session.get(CHAUFFEUR, driver_id)
            if driver is None:
                logging.warning("Aucun chauffeur trouvé avec l'id: %s", driver_id)
                return None

            for key, value in kwargs.items():
                if hasattr(driver, key):
                    setattr(driver, key, value)
                else:
                    logging.warning("L'attribut '%s' n'existe pas sur Chauffeur_Model", key)

            with my_session.begin():
                my_session.refresh(driver)

            return driver
        except SQLAlchemyError as e:
            logging.error("Erreur lors de la mise à jour du chauffeur (id=%s): %s", driver_id, e)
            raise e

    def delete_driver(self, driver_id):
        """
        Supprime un chauffeur par son identifiant.
        """
        try:
            driver = my_session.get(CHAUFFEUR, driver_id)
            if driver is None:
                logging.warning("Aucun chauffeur trouvé avec l'id: %s", driver_id)
                return False

            with my_session.begin():
                my_session.delete(driver)

            return True
        except SQLAlchemyError as e:
            logging.error("Erreur lors de la suppression du chauffeur (id=%s): %s", driver_id, e)
            raise e

    def search_chauffeur(self, nom=None, postnom=None, prenom=None):
        """
        Recherche des chauffeurs par nom, postnom ou prénom et récupère leurs photos associées.
        """
        try:
            query = my_session.query(CHAUFFEUR)
            if nom:
                query = query.filter(CHAUFFEUR.nom.ilike(f"%{nom}%"))
            if postnom:
                query = query.filter(CHAUFFEUR.postnom.ilike(f"%{postnom}%"))
            if prenom:
                query = query.filter(CHAUFFEUR.prenom.ilike(f"%{prenom}%"))

            chauffeurs = query.all()
            if not chauffeurs:
                logging.info("Aucun chauffeur trouvé pour les critères spécifiés.")
                return {"chauffeurs": [], "photos": []}

            chauffeur_ids = [chauffeur.id for chauffeur in chauffeurs]
            photos = my_session.query(IMAGE).filter(IMAGE.personne_id.in_(chauffeur_ids)).all()

            return {"chauffeurs": chauffeurs, "photos": photos}
        except SQLAlchemyError as e:
            logging.error(f"Erreur lors de la recherche des chauffeurs et des photos : {e}")
            return {"chauffeurs": [], "photos": []}
