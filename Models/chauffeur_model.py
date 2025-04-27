from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .personne_model import PERSONNE

class CHAUFFEUR(PERSONNE):
    __tablename__ = "chauffeurs"

    id = Column(Integer, ForeignKey("personnes.id"), primary_key=True)
    numero_permis = Column(String(50), unique=True, nullable=False)

    vehicules = relationship("VEHICULE", back_populates="chauffeur", cascade="all, delete-orphan")
    historiques = relationship("HISTORIQUE", back_populates="chauffeur", cascade="all, delete-orphan")
