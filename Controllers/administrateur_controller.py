from Models.administrateur_model import ADMINISTRATEUR
from Models.database_model import my_session
import logging
from sqlalchemy.exc import SQLAlchemyError
import bcrypt
from datetime import datetime


class ADMINISTRATEUR_CONTROLLER:

    def new_administrateur(self, username: str, password: str, created_at: datetime, last_login: datetime = None, is_active: bool = True, super_admin: bool = False):
        """Crée un nouvel administrateur après hachage du mot de passe."""
        try:
            if not username or not password:
                raise ValueError(
                    "Le nom d'utilisateur et le mot de passe sont requis.")

            # Vérifier si l'utilisateur existe déjà
            if self.get_administrateur_by_username(username):
                raise ValueError("Ce nom d'utilisateur est déjà utilisé.")

            # Hachage du mot de passe
            hashed_password = bcrypt.hashpw(password.encode(
                'utf-8'), bcrypt.gensalt()).decode('utf-8')

            # Création du nouvel administrateur
            new_admin = ADMINISTRATEUR(
                username=username,
                password_hash=hashed_password,
                created_at=created_at,
                last_login=last_login,
                is_active=is_active,
                super_admin=super_admin
            )

            my_session.add(new_admin)
            my_session.commit()
            my_session.refresh(new_admin)
            return True  # Indiquer le succès de l'enregistrement

        except ValueError as ve:
            logging.error(f"Erreur de validation : {str(ve)}")
            my_session.rollback()
            return False
        except SQLAlchemyError as sqle:
            logging.error(f"Erreur SQL : {str(sqle)}")
            my_session.rollback()
            return False
        except Exception as e:
            logging.error(f"Erreur inattendue : {str(e)}")
            my_session.rollback()
            return False

    def get_administrateur_by_username(self, username: str):
        """Récupère un administrateur par son nom d'utilisateur."""
        try:
            return my_session.query(ADMINISTRATEUR).filter_by(username=username).first()
        except Exception as e:
            logging.error(
                f"Erreur lors de la récupération de l'administrateur '{username}' : {str(e)}")
            return None

    def get_all_administrateurs(self):
        """Récupère tous les administrateurs."""
        try:
            return my_session.query(ADMINISTRATEUR).all()
        except Exception as e:
            logging.error(
                f"Erreur lors de la récupération des administrateurs : {str(e)}")
            return []
