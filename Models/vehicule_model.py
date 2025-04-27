from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .database_model import Base

class VEHICULE(Base):
    __tablename__ = "vehicules"

    id = Column(Integer, primary_key=True, index=True)
    couleur = Column(String(50), nullable=True)
    numero_plaque = Column(String(50), unique=True, nullable=False)
    marque = Column(String(50), nullable=False)
    modele = Column(String(50), nullable=True)
    annee = Column(Integer, nullable=True)

    chauffeur_id = Column(Integer, ForeignKey("chauffeurs.id"), nullable=False)
    chauffeur = relationship("CHAUFFEUR", back_populates="vehicules")
