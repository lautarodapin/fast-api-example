
from datetime import date, datetime
from pydantic import BaseModel


class Record(BaseModel):
    id: int
    date: date
    country: str
    cases: int
    deaths: int
    recoveries: int

    class Config:
        orm_mode = True


class PostRecord(BaseModel):
    date: date
    country: str
    cases: int
    deaths: int
    recoveries: int

    class Config:
        orm_mode = True



    
class UserIn(BaseModel):
    username: str
    password: str

    class Config:
        orm_mode = True
class User(UserIn):
    id: int

    class Config:
        orm_mode = True


class NotaIn(BaseModel):
    class Config:
        orm_mode = True
    titulo: str
    cuerpo: str
class Nota(NotaIn):
    class Config:
        orm_mode = True

    id: int
    titulo: str
    cuerpo: str
    created_at: datetime
    mod_at: datetime