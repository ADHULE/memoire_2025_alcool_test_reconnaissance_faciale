from sqlalchemy import Column, Integer, LargeBinary, ForeignKey
from sqlalchemy.orm import relationship
from .database_model import Base

class ENTRAINEMENT(Base):
    __tablename__ = "entrainement"
    
    id = Column(Integer, primary_key=True)
    model_data = Column(LargeBinary, nullable=False)  # Stocke le fichier YAML
    image_id = Column(Integer, ForeignKey("images.id"))  # Correction de la référence

    image = relationship("IMAGE", back_populates="entrainement")
