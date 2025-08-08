import logging
from Models.database_model import my_session
from Models.image_model import IMAGE

# Configuration du journal des logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IMAGE_CONTROLLER:
    """Gestion des opérations CRUD sur les images dans la base de données."""

    def __init__(self):
        self.session = my_session  #Correction de l'accès à la session

    @staticmethod
    def validate_input(value, field_name):
        """Valide qu'un champ obligatoire n'est pas vide ou invalide."""
        if not value or str(value).strip() == "":
            logger.warning(f"{field_name} est requis ou invalide.")
            return False
        return True

    # Ajouter une image
    def add_photo(self, url, personne_id):
        if not self.validate_input(url, "URL") or not self.validate_input(personne_id, "ID de la personne"):
            return None

        try:
            new_photo = IMAGE(url=url.strip(), personne_id=personne_id)
            self.session.add(new_photo)
            self.session.commit()
            self.session.refresh(new_photo)
            logger.info(f"Photo ajoutée avec succès : {new_photo}")
            return new_photo
        except Exception as e:
            self.session.rollback()
            logger.error(f"Erreur lors de l'ajout de la photo : {e}")
            return None

    # Récupérer une image par ID
    def get_photo(self, photo_id):
        if not self.validate_input(photo_id, "ID de la photo"):
            return None

        try:
            return self.session.query(IMAGE).filter_by(id=photo_id).first()
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de la photo : {e}")
            return None

    # Récupérer toutes les images
    def get_all_photos(self, limit=100):
        try:
            return self.session.query(IMAGE).limit(limit).all()
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des photos : {e}")
            return None

    # Mettre à jour une image
    def update_photo(self, photo_id, new_url=None, new_personne_id=None):
        if not self.validate_input(photo_id, "ID de la photo"):
            return None

        try:
            photo = self.session.query(IMAGE).filter_by(id=photo_id).first()
            if not photo:
                logger.info(f"Aucune photo trouvée avec l'ID {photo_id}.")
                return None

            if new_url:
                photo.url = new_url.strip()
            if new_personne_id:
                photo.personne_id = new_personne_id

            self.session.commit()
            logger.info(f"Photo mise à jour : {photo}")
            return photo
        except Exception as e:
            self.session.rollback()
            logger.error(f"Erreur lors de la mise à jour : {e}")
            return None

    # Supprimer une image par ID
    def delete_photo(self, photo_id):
        if not self.validate_input(photo_id, "ID de la photo"):
            return False

        try:
            photo = self.session.query(IMAGE).filter_by(id=photo_id).first()
            if not photo:
                return False

            self.session.delete(photo)
            self.session.commit()
            logger.info(f"Photo supprimée : {photo}")
            return True
        except Exception as e:
            self.session.rollback()
            logger.error(f"Erreur lors de la suppression de la photo : {e}")
            return False

    # Supprimer une image par son chemin (URL)
    def delete_photo_by_path(self, image_path):
        if not self.validate_input(image_path, "Chemin de l'image"):
            return False

        try:
            photo = self.session.query(IMAGE).filter_by(url=image_path).first()
            if not photo:
                return False

            self.session.delete(photo)
            self.session.commit()
            logger.info(f"Photo supprimée par chemin : {image_path}")
            return True
        except Exception as e:
            self.session.rollback()
            logger.error(f"Erreur lors de la suppression par chemin : {e}")
            return False

    # Méthode manquante corrigée
    def get_image_path_by_id(self, image_id):
        if not self.validate_input(image_id, "ID de l'image"):
            return None
        try:
            image = self.session.query(IMAGE).filter_by(id=image_id).first()
            return image.url if image else None
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du chemin de l'image : {e}")
            return None
