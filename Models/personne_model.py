from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from .database_model import Base

class PERSONNE(Base):
    __tablename__ = "personnes"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(255), nullable=False)
    postnom = Column(String(255), nullable=False)
    prenom = Column(String(255), nullable=True)
    telephone = Column(String(20), nullable=False)
    email = Column(String(255), unique=True, nullable=True)
    sex=Column(String(10),unique=True,nullable=True)

    # Relation avec Image
    images = relationship("IMAGE", back_populates="personne", cascade="all, delete-orphan")
