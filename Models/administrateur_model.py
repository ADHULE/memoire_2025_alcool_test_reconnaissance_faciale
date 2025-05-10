from sqlalchemy import Column, Integer, String, DateTime, Boolean
from Models.database_model import Base

class ADMINISTRATEUR(Base):
    __tablename__ = "administrateurs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    role = Column(String(50), nullable=False, default="administrateur")
    created_at = Column(DateTime, nullable=False)
    last_login = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    super_admin = Column(Boolean, default=False)