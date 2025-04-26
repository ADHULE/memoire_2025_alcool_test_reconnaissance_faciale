from Models.database_model import my_session
from Models.chaffeur_model import Chauffeur_Model  # Remarquez l'orthographe utilisée dans votre projet
from sqlalchemy.exc import SQLAlchemyError
import logging

# Assurez-vous que le module de logging est configuré dans votre application.
logging.basicConfig(level=logging.INFO)

class Chauffeur_Controller:
    """
    Contrôleur pour gérer les opérations CRUD sur les objets Chauffeur.
    """

    def new_Driver(self, nom, postnom, prenom, telephone, email, numero_permis):
        """
        Crée un nouveau chauffeur et l'enregistre en base de données.
        """
        try:
            new_driver = Chauffeur_Model(
                nom=nom,
                postnom=postnom,
                prenom=prenom,
                telephone=telephone,
                email=email,
                numero_permis=numero_permis,
            )
            my_session.add(new_driver)
            my_session.commit()
            my_session.refresh(new_driver)
            return new_driver
        except SQLAlchemyError as e:
            my_session.rollback()
            logging.error("Erreur lors de la création du chauffeur: %s", e)
            # Vous pouvez choisir de remonter l'erreur ou retourner None
            raise e

    def get_driver(self, driver_id):
        """
        Récupère un chauffeur par son identifiant.
        """
        try:
            # Note : .get() est simple à utiliser mais peut être remplacé par session.get() sur SQLAlchemy 1.4+
            driver = my_session.query(Chauffeur_Model).get(driver_id)
            if driver is None:
                logging.warning("Aucun chauffeur trouvé avec l'id: %s", driver_id)
            return driver
        except SQLAlchemyError as e:
            my_session.rollback()
            logging.error("Erreur lors de la récupération du chauffeur (id=%s): %s", driver_id, e)
            raise e

    def get_all_drivers(self):
        """
        Récupère tous les chauffeurs présents en base de données.
        """
        try:
            drivers = my_session.query(Chauffeur_Model).all()
            return drivers
        except SQLAlchemyError as e:
            my_session.rollback()
            logging.error("Erreur lors de la récupération de tous les chauffeurs: %s", e)
            raise e

    def update_driver(self, driver_id, **kwargs):
        """
        Met à jour les attributs d'un chauffeur existant.
        Les modifications sont passées sous forme de kwargs.
        Exemple d'appel : update_driver(1, telephone="0123456789", email="nouveau@mail.com")
        """
        try:
            driver = my_session.query(Chauffeur_Model).get(driver_id)
            if driver is None:
                logging.warning("Aucun chauffeur trouvé avec l'id: %s", driver_id)
                return None

            # Mise à jour des attributs existants
            for key, value in kwargs.items():
                if hasattr(driver, key):
                    setattr(driver, key, value)
                else:
                    logging.warning("L'attribut '%s' n'existe pas sur Chauffeur_Model", key)

            my_session.commit()
            my_session.refresh(driver)
            return driver
        except SQLAlchemyError as e:
            my_session.rollback()
            logging.error("Erreur lors de la mise à jour du chauffeur (id=%s): %s", driver_id, e)
            raise e

    def delete_driver(self, driver_id):
        """
        Supprime un chauffeur par son identifiant.
        Renvoie True si la suppression réussit, False si le chauffeur n'existe pas.
        """
        try:
            driver = my_session.query(Chauffeur_Model).get(driver_id)
            if driver is None:
                logging.warning("Aucun chauffeur trouvé avec l'id: %s", driver_id)
                return False

            my_session.delete(driver)
            my_session.commit()
            return True
        except SQLAlchemyError as e:
            my_session.rollback()
            logging.error("Erreur lors de la suppression du chauffeur (id=%s): %s", driver_id, e)
            raise e
