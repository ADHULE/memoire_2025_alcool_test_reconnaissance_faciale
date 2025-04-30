from Models.administrateur_model import ADMINISTRATEUR
from Models.database_model import my_session
import logging
from sqlalchemy import select
import bcrypt # Importez la bibliothèque bcrypt pour le hachage

class ADMINISTRATEUR_CONTROLLER:

    def new_administrateur(
        self,
        nom: str,
        postnom: str,
        prenom: str,
        telephone: int,
        email,
        username: str,
        password: str,  # Acceptez le mot de passe en clair
        role: str,
        created_at,
        last_login,
        is_active=False,
        super_admin=False,
    ):
        try:
            # Hacher le mot de passe si fourni
            if password:
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            else:
                # Gérer le cas où aucun mot de passe n'est fourni.
                # Cela dépend de votre logique d'enregistrement.
                # Ici, nous levons une ValueError car password_hash ne peut pas être nul.
                raise ValueError("Le mot de passe doit être fourni pour l'enregistrement.")

            new_admin = ADMINISTRATEUR(
                nom=nom,
                postnom=postnom,
                prenom=prenom,
                telephone=telephone,
                email=email,
                username=username,
                password_hash=hashed_password,  # Utilisez le mot-clé correct
                role=role,
                created_at=created_at,
                last_login=last_login,
                is_active=is_active,
                super_admin=super_admin,
            )
            my_session.add(new_admin)
            my_session.commit()
            my_session.refresh(new_admin)
            return new_admin
        except ValueError as ve:
            logging.error(f"Erreur lors de l'enregistrement de nouveau administrateur: {str(ve)}")
            my_session.rollback()
            return None
        except Exception as e:
            logging.error(
                f"Erreur lors de l'enregistrement de nouveau administrateur: {str(e)}"
            )
            my_session.rollback()
            return None

    def activate_administrateur(self, admin_id):
        """Active un administrateur."""
        admin = my_session.query(ADMINISTRATEUR).get(admin_id)
        if admin:
            admin.is_active = True
            my_session.commit()
            return True
        return False

    def get_administrateur_by_id(self, admin_id: int):
        try:
            statement = select(ADMINISTRATEUR).where(ADMINISTRATEUR.id == admin_id)
            administrateur = my_session.execute(statement).scalar_one_or_none()
            return administrateur
        except Exception as e:
            logging.error(
                f"Erreur lors de la récupération de l'administrateur avec l'ID {admin_id}: {str(e)}"
            )
            return None

    def get_administrateur_by_username(self, username: str):
        try:
            statement = select(ADMINISTRATEUR).where(
                ADMINISTRATEUR.username == username
            )
            administrateur = my_session.execute(statement).scalar_one_or_none()
            return administrateur
        except Exception as e:
            logging.error(
                f"Erreur lors de la récupération de l'administrateur avec le nom d'utilisateur '{username}': {str(e)}"
            )
            return None

    def get_all_administrateurs(self):
        try:
            statement = select(ADMINISTRATEUR)
            administrateurs = my_session.execute(statement).scalars().all()
            return list(administrateurs)
        except Exception as e:
            logging.error(
                f"Erreur lors de la récupération de tous les administrateurs: {str(e)}"
            )
            return []

    def update_administrateur(self, admin_id: int, **kwargs):
        try:
            administrateur = self.get_administrateur_by_id(admin_id)
            if administrateur:
                for key, value in kwargs.items():
                    if hasattr(administrateur, key):
                        setattr(administrateur, key, value)
                my_session.commit()
                my_session.refresh(administrateur)
                return administrateur
            return None
        except Exception as e:
            logging.error(
                f"Erreur lors de la mise à jour de l'administrateur avec l'ID {admin_id}: {str(e)}"
            )
            my_session.rollback()
            return None

    def delete_administrateur(self, admin_id: int):
        try:
            administrateur = self.get_administrateur_by_id(admin_id)
            if administrateur:
                my_session.delete(administrateur)
                my_session.commit()
                return True
            return False
        except Exception as e:
            logging.error(
                f"Erreur lors de la suppression de l'administrateur avec l'ID {admin_id}: {str(e)}"
            )
            my_session.rollback()
            return False