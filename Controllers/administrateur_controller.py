from Models.administrateur_model import ADMINISTRATEUR
from Models.database_model import my_session
from sqlalchemy.exc import SQLAlchemyError
import bcrypt
from datetime import datetime
import logging
import traceback

class ADMINISTRATEUR_CONTROLLER:
    def new_administrateur(self, username, password, role=None, is_active=True, super_admin=False):
        try:
            if not username or not password:
                raise ValueError("Nom d'utilisateur et mot de passe requis.")
            if self.get_administrateur_by_username(username):
                raise ValueError("Nom d'utilisateur déjà utilisé.")

            password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            admin = ADMINISTRATEUR(
                username=username,
                password_hash=password_hash,
                role=role,
                is_active=is_active,
                super_admin=super_admin,
                created_at=datetime.now()
            )
            my_session.add(admin)
            my_session.commit()
            my_session.refresh(admin)
            return admin

        except Exception as e:
            logging.error(f"Erreur création administrateur : {str(e)}\n{traceback.format_exc()}")
            my_session.rollback()
            return None

    def get_administrateur_by_username(self, username):
        try:
            return my_session.query(ADMINISTRATEUR).filter_by(username=username).first()
        except Exception as e:
            logging.error(f"Erreur récupération par nom : {str(e)}")
            return None

    def update_last_login(self, username):
        try:
            admin = self.get_administrateur_by_username(username)
            if admin:
                admin.last_login = datetime.now()
                my_session.commit()
                return True
            return False
        except Exception as e:
            logging.error(f"Erreur mise à jour last_login : {str(e)}")
            my_session.rollback()
            return False

    def get_all_administrateurs(self):
        try:
            return my_session.query(ADMINISTRATEUR).all()
        except Exception as e:
            logging.error(f"Erreur récupération liste : {str(e)}")
            return []

    def delete_administrateur(self, admin_id):
        try:
            admin = my_session.query(ADMINISTRATEUR).filter_by(id=admin_id).first()
            if not admin:
                raise ValueError("Administrateur introuvable.")
            my_session.delete(admin)
            my_session.commit()
            return True
        except Exception as e:
            logging.error(f"Erreur suppression : {str(e)}")
            my_session.rollback()
            return False

    def filter_administrateurs(self, username=None, role=None, is_active=None, super_admin=None):
        """Filtre les administrateurs selon les critères fournis."""
        try:
            query = my_session.query(ADMINISTRATEUR)

            if username:
                query = query.filter(ADMINISTRATEUR.username.ilike(f"%{username}%"))
            if role:
                query = query.filter(ADMINISTRATEUR.role == role)
            if is_active is not None:
                query = query.filter(ADMINISTRATEUR.is_active == is_active)
            if super_admin is not None:
                query = query.filter(ADMINISTRATEUR.super_admin == super_admin)

            return query.all()

        except SQLAlchemyError as error:
            logging.error(f"Erreur filtrage : {str(error)}")
            return []

