from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from .database_model import Base

class HISTORIQUE(Base):
    __tablename__ = "historiques"

    id = Column(Integer, primary_key=True, index=True)
    chauffeur_id = Column(Integer, ForeignKey('chauffeurs.id'), nullable=False)
    jour_heure = Column(DateTime, nullable=False)
    event_type = Column(String(50), nullable=False)
   
    chauffeur = relationship("CHAUFFEUR", back_populates="historiques")
