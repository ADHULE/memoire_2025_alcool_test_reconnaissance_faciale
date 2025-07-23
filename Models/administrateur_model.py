from sqlalchemy import Column, Integer, String, Boolean, DateTime
from Models.database_model import Base
from datetime import datetime

class ADMINISTRATEUR(Base):
    __tablename__ = "administrateurs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    role = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)
    super_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    last_login = Column(DateTime, nullable=True)
