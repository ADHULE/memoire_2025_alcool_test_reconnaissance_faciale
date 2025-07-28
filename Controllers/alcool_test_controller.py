from Models.test_alcool_save_model import AlcoolTestModel
from Models.database_model import my_session

class AlcoolTestController:

    def new_alcool_value(self, datte, valeur):
        """Création d'un nouveau test alcool"""
        try:
            new_alcool = AlcoolTestModel(datte=datte, valeur=valeur)
            my_session.add(new_alcool)
            my_session.commit()
            my_session.refresh(new_alcool)
            print(f"[DB] Sauvegardé : {valeur} à {datte}")
        except Exception as e:
            print(f"[DB ERROR] Création échouée : {e}")
            my_session.rollback()

    def get_all_values(self):
        """Lire tous les enregistrements"""
        try:
            return my_session.query(AlcoolTestModel).order_by(AlcoolTestModel.datte.desc()).all()
        except Exception as e:
            print(f"[DB ERROR] Lecture échouée : {e}")
            return []

    def get_value_by_id(self, record_id):
        """Lire un seul enregistrement par ID"""
        try:
            return my_session.get(AlcoolTestModel, record_id)
        except Exception as e:
            print(f"[DB ERROR] Lecture par ID échouée : {e}")
            return None

    def update_value(self, record_id, new_valeur):
        """Mettre à jour un test existant"""
        try:
            item = my_session.get(AlcoolTestModel, record_id)
            if item:
                item.valeur = new_valeur
                my_session.commit()
                my_session.refresh(item)
                print(f"[DB] Mis à jour ID {record_id} → {new_valeur}")
            else:
                print(f"[DB WARNING] Aucun enregistrement trouvé avec ID {record_id}")
        except Exception as e:
            print(f"[DB ERROR] Mise à jour échouée : {e}")
            my_session.rollback()

    def delete_value(self, record_id):
        """Supprimer un test alcool par ID"""
        try:
            item = my_session.get(AlcoolTestModel, record_id)
            if item:
                my_session.delete(item)
                my_session.commit()
                print(f"[DB] Supprimé ID {record_id}")
            else:
                print(f"[DB WARNING] Aucun enregistrement à supprimer avec ID {record_id}")
        except Exception as e:
            print(f"[DB ERROR] Suppression échouée : {e}")
            my_session.rollback()
