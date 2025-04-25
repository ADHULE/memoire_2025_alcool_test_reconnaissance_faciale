from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from Models.database_model import Base

class Vehicule_Model(Base):
    __tablename__ = "vehicules"
    
    id = Column(Integer, primary_key=True, index=True)
    couleur = Column(String(50), nullable=True)
    numero_plaque = Column(String(50), unique=True, nullable=False)
    marque = Column(String(50), nullable=False)
    modele = Column(String(50), nullable=True)
    annee = Column(Integer, nullable=True)
    
    # Relation vers le chauffeur qui conduit le véhicule
    chauffeur_id = Column(Integer, ForeignKey("chauffeurs.id"), nullable=False)
    
    # Relationship avec le modèle Chauffeur_Model
    chauffeur = relationship("Chauffeur_Model", back_populates="vehicules")
