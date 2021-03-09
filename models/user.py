from sqlalchemy import Column, Integer, String
from sqlalchemy.sql.expression import null
from sqlalchemy.types import Date
from werkzeug.security import generate_password_hash, check_password_hash

from database import Base

class User(Base):
    __tablename__ = "Users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), nullable=False, unique=True)
    password = Column(String(500), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)