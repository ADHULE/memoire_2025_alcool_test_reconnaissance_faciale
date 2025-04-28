from Models.image_model import IMAGE
from Models.database_model import my_session
import logging
from Controllers.chauffeur_controller import CHAUFFEUR_CONTROLLER

# Configuration de la journalisation
logging.basicConfig(level=logging.INFO)


class IMAGE_CONTROLLER:
    def __init__(self):
        """
        Initialise le Photocontroller et crée une instance de EtudiantController.
        """
        self.chauffeur_controller = CHAUFFEUR_CONTROLLER()

    @staticmethod
    def validate_input(value, field_name):
        """
        Valide qu'un champ obligatoire n'est pas vide ou invalide.
        """
        if not value or str(value).strip() == "":
            logging.warning(f"{field_name} est requis ou invalide.")
            return False
        return True

    # Fonction CREATE
    def add_photo(self, url, personne_id):
        """
        Ajoute une nouvelle photo dans la base de données.
        """
        if not self.validate_input(url, "URL") or not self.validate_input(personne_id, "ID de la personne"):
            return None

        try:
            new_photo = IMAGE(url=url.strip(), personne_id=personne_id)
            my_session.add(new_photo)
            my_session.commit()
            my_session.refresh(new_photo)
            logging.info(f"Photo ajoutée avec succès : {new_photo}")
            return new_photo
        except Exception as e:
            my_session.rollback()
            logging.error(f"Erreur lors de l'ajout de la photo : {e}")
            return None

    # Fonction READ
    def get_photo(self, photo_id):
        """
        Récupère une photo à partir de son ID.
        """
        if not self.validate_input(photo_id, "ID de la photo"):
            return None

        try:
            photo = my_session.query(IMAGE).filter_by(id=photo_id).first()
            if not photo:
                logging.info(f"Aucune photo trouvée avec l'ID {photo_id}.")
                return None
            return photo
        except Exception as e:
            logging.error(f"Erreur lors de la récupération de la photo : {e}")
            return None

    def get_all_photos(self, limit=100):
        """
        Récupère toutes les photos avec une limite.
        """
        try:
            photos = my_session.query(IMAGE).limit(limit).all()
            # logging.info(f"{len(photos)} photo(s) récupérée(s) avec succès.")
            return photos
        except Exception as e:
            logging.error(f"Erreur lors de la récupération des photos : {e}")
            return None

    def filter_photos_by_person_info(self, nom=None, postnom=None, prenom=None):
        """
        Filtre les photos par les informations de la personne associée.
        """
        try:
            personnes = self.chauffeur_controller.search_chauffeur(nom=nom, postnom=postnom, prenom=prenom)
            personne_ids = [personne.id for personne in personnes if personne.id]

            if not personne_ids:
                logging.info("Aucune personne trouvée avec ces informations.")
                return []

            filtered_photos = my_session.query(IMAGE).filter(IMAGE.personne_id.in_(personne_ids)).all()
            # logging.info(f"{len(filtered_photos)} photo(s) trouvée(s).")
            return filtered_photos
        except Exception as e:
            logging.error(f"Erreur lors du filtrage : {e}")
            return None

    # Fonction UPDATE
    def update_photo(self, photo_id, new_url=None, new_personne_id=None):
        """
        Met à jour une photo existante dans la base de données.
        """
        if not self.validate_input(photo_id, "ID de la photo"):
            return None

        try:
            photo = my_session.query(IMAGE).filter_by(id=photo_id).first()
            if not photo:
                logging.info(f"Aucune photo trouvée avec l'ID {photo_id}.")
                return None

            if new_url:
                photo.url = new_url.strip()
            if new_personne_id:
                photo.personne_id = new_personne_id

            my_session.commit()
            # logging.info(f"Photo mise à jour avec succès : {photo}")
            return photo
        except Exception as e:
            my_session.rollback()
            logging.error(f"Erreur lors de la mise à jour de la photo : {e}")
            return None

    # Fonction DELETE
    def delete_photo(self, photo_id):
        """
        Supprime une photo de la base de données.
        """
        if not self.validate_input(photo_id, "ID de la photo"):
            return False

        try:
            photo = my_session.query(IMAGE).filter_by(id=photo_id).first()
            if not photo:
                # logging.info(f"Aucune photo trouvée avec l'ID {photo_id}.")
                return False

            my_session.delete(photo)
            my_session.commit()
            # logging.info(f"Photo avec l'ID {photo_id} supprimée avec succès.")
            return True
        except Exception as e:
            my_session.rollback()
            logging.error(f"Erreur lors de la suppression de la photo : {e}")
            return False

    def delete_photo_by_path(self, image_path):
        """
        Supprime une photo de la base de données en fonction de son chemin (URL).
        """
        if not self.validate_input(image_path, "Chemin de l'image"):
            return False

        try:
            photo = my_session.query(IMAGE).filter_by(url=image_path).first()
            if not photo:
                # logging.info(f"Aucune photo trouvée avec le chemin '{image_path}'.")
                return False

            my_session.delete(photo)
            my_session.commit()
            # logging.info(f"Photo avec le chemin '{image_path}' supprimée avec succès.")
            return True
        except Exception as e:
            my_session.rollback()
            logging.error(f"Erreur lors de la suppression de la photo par chemin : {e}")
            return False

    def search_photos(self, text):
        """
        Recherche des photos dont l'URL contient le texte spécifié.
        """
        try:
            filtered_photos = my_session.query(IMAGE).filter(IMAGE.url.ilike(f"%{text}%")).all()
            # logging.info(f"{len(filtered_photos)} photo(s) trouvée(s) correspondant à la recherche '{text}'.")
            return filtered_photos
        except Exception as e:
            logging.error(f"Erreur lors de la recherche des photos : {e}")
            return None
