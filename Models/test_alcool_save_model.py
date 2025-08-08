from sqlalchemy import Column, Integer, DateTime, Float

from Models.database_model import Base


class AlcoolTestModel(Base):
    __tablename__ = 'alcool_test_model'
    id = Column(Integer, primary_key=True, index=True)
    datte=Column(DateTime, nullable=False)
    valeur = Column(Float, nullable=False)
