from sqlalchemy import Column, Integer, String
from sqlalchemy.types import Date
from database import Base

class Nota(Base):
    __tablename__ = "Notas"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255))
    titulo = Column(String(100), nullable=False, unique=True)
    password = Column(String(500))