from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from Models.database_model import Base

class Historique_Model(Base):
    __tablename__ = "historiques"
    id = Column(Integer, primary_key=True, index=True)
    
    # Clé étrangère corrigée vers 'chauffeurs'
    chauffeur_id = Column(Integer, ForeignKey('chauffeurs.id'), nullable=False)
    
    # Date et heure de l'enregistrement de l'événement
    jour_heure = Column(DateTime, nullable=False)
    
    # Type d'événement, par exemple, "alcootest", "reconnaissance faciale", etc.
    event_type = Column(String(50), nullable=False)
    
    # Résultat de l'événement, par exemple, "passé", "échoué"
    result = Column(String(50), nullable=True)
    
    # Commentaire facultatif pour stocker des informations supplémentaires
    commentaire = Column(Text, nullable=True)
    
    # Relation bidirectionnelle avec Chauffeur_Model
    chauffeur = relationship("Chauffeur_Model", back_populates="historiques")
