from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.sql.expression import null
from sqlalchemy.types import Date, DateTime
from sqlalchemy.sql import func
from database import Base

class Nota(Base):
    __tablename__ = "Notas"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(100), nullable=False, unique=True)
    cuerpo = Column(Text(5000), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    mod_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.current_timestamp())