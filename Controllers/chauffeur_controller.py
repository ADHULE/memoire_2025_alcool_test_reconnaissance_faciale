from Models.chauffeur_model import CHAUFFEUR
from Models.database_model import my_session


class CHAUFFEUR_CONTROLLER:
    def new_driver(self, nom, postnom, prenom, telephone, email, numero_permis,sex):
        """🔹 Créer un chauffeur."""
        try:
            new_chauffeur = CHAUFFEUR(
                nom=nom,
                postnom=postnom,
                prenom=prenom,
                telephone=telephone,
                email=email,
                numero_permis=numero_permis,
                sex=sex,
            )

            my_session.add(new_chauffeur)
            my_session.commit()
            my_session.refresh(new_chauffeur)
            return new_chauffeur
        except Exception as e:
            print(f"Erreur d'enregistrement du chauffeur : {str(e)}")
            return None

    def get_all_drivers(self):
        """🔹 Récupérer tous les chauffeurs."""
        try:

            return my_session.query(CHAUFFEUR).all()
        except Exception as e:
            print(f"Erreur de récupération des chauffeurs : {str(e)}")
            return []

    def get_driver_by_id(self, chauffeur_id):
        """🔹 Récupérer un chauffeur par son identifiant."""
        try:
            chauffeur = my_session.query(CHAUFFEUR).filter(CHAUFFEUR.id == chauffeur_id).first()
            return chauffeur
        except Exception as e:
            print(f"Erreur de récupération du chauffeur : {str(e)}")
            return None

    def update_driver(
        self,
        chauffeur_id,
        nom=None,
        postnom=None,
        prenom=None,
        telephone=None,
        email=None,
        numero_permis=None,
        sex=None
    ):
        """🔹 Mettre à jour un chauffeur."""
        try:

            chauffeur = (
                my_session.query(CHAUFFEUR).filter(CHAUFFEUR.id == chauffeur_id).first()
            )
            if not chauffeur:
                return None

            if nom:
                chauffeur.nom = nom
            if postnom:
                chauffeur.postnom = postnom
            if prenom:
                chauffeur.prenom = prenom
            if telephone:
                chauffeur.telephone = telephone
            if email:
                chauffeur.email = email
            if numero_permis:
                chauffeur.numero_permis = numero_permis
            if sex:
                chauffeur.sex=sex
            my_session.commit()
            my_session.refresh(chauffeur)
            return chauffeur
        except Exception as e:
            print(f"Erreur de mise à jour : {str(e)}")
            return None

    def delete_driver(self, chauffeur_id):
        """🔹 Supprimer un chauffeur."""
        try:

            chauffeur = (
                my_session.query(CHAUFFEUR).filter(CHAUFFEUR.id == chauffeur_id).first()
            )
            if not chauffeur:
                return False

            my_session.delete(chauffeur)
            my_session.commit()
            return True
        except Exception as e:
            print(f"Erreur de suppression : {str(e)}")
            return False
