from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .database_model import Base

class Image(Base):
    __tablename__ = 'images'
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(255), nullable=False)
    # La clé étrangère est marquée comme non nullable pour assurer l'intégrité référentielle
    personne_id = Column(Integer, ForeignKey('personnes.id'), nullable=False)
    personne = relationship('Personne', back_populates='images')
