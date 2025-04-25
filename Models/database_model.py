from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
# Définir la classe de base
Base = declarative_base()

# Créer l'URL de connexion
USERNAME = 'root'
PASSWORD = ''  # Mettre un mot de passe sécurisé
HOST = 'localhost'
PORT = '3306'
DB_NAME = 'enregistrement_chauffeurs'

DATABASE_URL = f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)

# Optionnel : création d'une session
Session = sessionmaker(bind=engine)
my_session = Session()
