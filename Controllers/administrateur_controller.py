from Models.administrateur_model import ADMINISTRATEUR
from Models.database_model import my_session
import logging
from sqlalchemy.exc import SQLAlchemyError
import bcrypt
from datetime import datetime

class ADMINISTRATEUR_CONTROLLER:

    def new_administrateur(self, username: str, password: str, role: str = None, is_active: bool = False, super_admin: bool = False):
        """Crée un nouvel administrateur."""
        try:
            if not username or not password:
                raise ValueError("Nom d'utilisateur et mot de passe requis.")

            if self.get_administrateur_by_username(username):
                raise ValueError("Nom d'utilisateur déjà utilisé.")

            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            new_admin = ADMINISTRATEUR(
                username=username,
                password_hash=hashed_password,
                role=role,
                is_active=is_active,
                super_admin=super_admin
            )

            my_session.add(new_admin)
            my_session.commit()
            my_session.refresh(new_admin)
            return new_admin

        except (ValueError, SQLAlchemyError) as error:
            logging.error(f"Erreur : {str(error)}")
            my_session.rollback()
            return None

    def get_administrateur_by_id(self, admin_id: int):
        """Récupère un administrateur par son ID."""
        return my_session.query(ADMINISTRATEUR).filter_by(id=admin_id).first()

    def get_administrateur_by_username(self, username: str):
        """Récupère un administrateur par son nom d'utilisateur."""
        return my_session.query(ADMINISTRATEUR).filter_by(username=username).first()

    def update_administrateur(self, admin_id: int, **kwargs):
        """Met à jour les informations d'un administrateur."""
        try:
            admin = self.get_administrateur_by_id(admin_id)
            if not admin:
                raise ValueError("Administrateur non trouvé.")

            for key, value in kwargs.items():
                if hasattr(admin, key):
                    setattr(admin, key, value)

            my_session.commit()
            return admin

        except (ValueError, SQLAlchemyError) as error:
            logging.error(f"Erreur mise à jour : {str(error)}")
            my_session.rollback()
            return None

    def delete_administrateur(self, admin_id: int):
        """Supprime un administrateur."""
        try:
            admin = self.get_administrateur_by_id(admin_id)
            if not admin:
                raise ValueError("Administrateur introuvable.")

            my_session.delete(admin)
            my_session.commit()
            return True

        except (ValueError, SQLAlchemyError) as error:
            logging.error(f"Erreur suppression : {str(error)}")
            my_session.rollback()
            return False

    def get_all_administrateurs(self):
        """Récupère tous les administrateurs."""
        return my_session.query(ADMINISTRATEUR).all()

    def filter_administrateurs(self, role=None, is_active=None, super_admin=None):
        """Filtre les administrateurs selon leur rôle, statut actif ou super admin."""
        try:
            query = my_session.query(ADMINISTRATEUR)
            if role:
                query = query.filter_by(role=role)
            if is_active is not None:
                query = query.filter_by(is_active=is_active)
            if super_admin is not None:
                query = query.filter_by(super_admin=super_admin)

            return query.all()

        except SQLAlchemyError as error:
            logging.error(f"Erreur filtrage : {str(error)}")
            return []

    def update_last_login(self, username: str):
        """Met à jour la dernière connexion d'un administrateur."""
        try:
            admin = self.get_administrateur_by_username(username)
            if admin:
                admin.last_login = datetime.now()
                my_session.commit()
                return True
            return False

        except SQLAlchemyError as error:
            logging.error(f"Erreur mise à jour du login : {str(error)}")
            my_session.rollback()
            return False
