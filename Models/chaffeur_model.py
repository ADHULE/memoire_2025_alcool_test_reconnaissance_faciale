from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .personne_model import Personne_Model

class Chauffeur_Model(Personne_Model):
    __tablename__ = "chauffeurs"

    id = Column(Integer, ForeignKey("personnes.id"), primary_key=True)
    numero_permis = Column(String(50), unique=True, nullable=False)

    # Un chauffeur peut conduire plusieurs véhicules
    vehicules = relationship(
        "Vehicule_Model", back_populates="chauffeur", cascade="all, delete-orphan"
    )

    # Relation avec les historiques (déjà en place)
    historiques = relationship(
        "Historique_Model", back_populates="chauffeur", cascade="all, delete-orphan"
    )
