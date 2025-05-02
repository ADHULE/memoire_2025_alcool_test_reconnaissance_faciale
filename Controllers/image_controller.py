import logging
from Models.image_model import IMAGE
from Models.database_model import my_session

# Configuration du journal des logs
logging.basicConfig(level=logging.INFO)

class IMAGE_CONTROLLER:
    """Gestion des opérations CRUD sur les images dans la base de données."""

    @staticmethod
    def validate_input(value, field_name):
        """Valide qu'un champ obligatoire n'est pas vide ou invalide."""
        if not value or str(value).strip() == "":
            logging.warning(f"{field_name} est requis ou invalide.")
            return False
        return True

    # CREATE - Ajouter une image
    def add_photo(self, url, personne_id):
        """Ajoute une nouvelle photo dans la base de données."""
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

    # READ - Récupérer une image par ID
    def get_photo(self, photo_id):
        """Récupère une photo à partir de son ID."""
        if not self.validate_input(photo_id, "ID de la photo"):
            return None

        try:
            return my_session.query(IMAGE).filter_by(id=photo_id).first()
        except Exception as e:
            logging.error(f"Erreur lors de la récupération de la photo : {e}")
            return None

    # READ - Récupérer toutes les images
    def get_all_photos(self, limit=100):
        """Récupère toutes les photos avec une limite."""
        try:
            return my_session.query(IMAGE).limit(limit).all()
        except Exception as e:
            logging.error(f"Erreur lors de la récupération des photos : {e}")
            return None

    # UPDATE - Mettre à jour une image
    def update_photo(self, photo_id, new_url=None, new_personne_id=None):
        """Met à jour une photo existante dans la base de données."""
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
            return photo
        except Exception as e:
            my_session.rollback()
            logging.error(f"Erreur lors de la mise à jour de la photo : {e}")
            return None

    # DELETE - Supprimer une image par ID
    def delete_photo(self, photo_id):
        """Supprime une photo de la base de données."""
        if not self.validate_input(photo_id, "ID de la photo"):
            return False

        try:
            photo = my_session.query(IMAGE).filter_by(id=photo_id).first()
            if not photo:
                return False

            my_session.delete(photo)
            my_session.commit()
            return True
        except Exception as e:
            my_session.rollback()
            logging.error(f"Erreur lors de la suppression de la photo : {e}")
            return False

    # DELETE - Supprimer une image par son chemin (URL)
    def delete_photo_by_path(self, image_path):
        """Supprime une photo en fonction de son URL."""
        if not self.validate_input(image_path, "Chemin de l'image"):
            return False

        try:
            photo = my_session.query(IMAGE).filter_by(url=image_path).first()
            if not photo:
                return False

            my_session.delete(photo)
            my_session.commit()
            return True
        except Exception as e:
            my_session.rollback()
            logging.error(f"Erreur lors de la suppression de la photo par chemin : {e}")
            return False
