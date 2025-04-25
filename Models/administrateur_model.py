from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .personne_model import Personne_Model

class Administrateur_Model(Personne_Model):
    __tablename__ = "administrateurs"
    
    # Clé primaire et clé étrangère pointant vers la table de base "personnes"
    id = Column(Integer, ForeignKey("personnes.id"), primary_key=True)
    
    # Nom d'utilisateur unique pour l'administrateur
    username = Column(String(50), unique=True, nullable=False)
    
    # Stockage du hash du mot de passe pour la sécurité
    password_hash = Column(String(128), nullable=False)
    
    # Rôle de l'administrateur (par défaut "administrateur", mais modulable)
    role = Column(String(50), nullable=False, default="administrateur")
    
    # Date de création du compte administrateur
    created_at = Column(DateTime, nullable=False)
    
    # Date du dernier accès, utile pour des statistiques ou la sécurité
    last_login = Column(DateTime, nullable=True)
    
    # Indicateur si l'administrateur est actif (pour active/désactiver le compte)
    is_active = Column(Boolean, default=True)
    
    # Optionnel : Indicateur si l'administrateur possède des privilèges élevés (super admin)
    super_admin = Column(Boolean, default=False)
