from sqlalchemy import Column, Integer, String
from sqlalchemy.types import Date
from database import Base

class User(Base):
    __tablename__ = "Users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255))
    password = Column(String(500))