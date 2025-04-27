from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .database_model import Base

class IMAGE(Base):
    __tablename__ = 'images'

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(255), nullable=False)

    personne_id = Column(Integer, ForeignKey('personnes.id'), nullable=False)
    personne = relationship('PERSONNE', back_populates='images')
