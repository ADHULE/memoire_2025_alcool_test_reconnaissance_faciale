from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Float
from sqlalchemy.orm import relationship
from .database_model import Base

class HISTORIQUE(Base):
    __tablename__ = "historiques"

    id = Column(Integer, primary_key=True, index=True)
    chauffeur_id = Column(Integer, ForeignKey('chauffeurs.id'), nullable=False)
    image_id = Column(Integer, ForeignKey('images.id'), nullable=True)  # 👈 Référence vers l'image
    jour_heure = Column(DateTime, nullable=False)
    event_type = Column(String(255), nullable=False)
    person_info = Column(String(255), nullable=False)
    alcool_value = Column(Float, nullable=False)

    chauffeur = relationship("CHAUFFEUR", back_populates="historiques")
    image = relationship("IMAGE", back_populates="historique")  # ⬅ Relation bidirectionnelle
