
from datetime import date, datetime
from pydantic import BaseModel, Field


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
    titulo: str = Field(..., example="Nota libertaria")
    cuerpo: str = Field(..., example="Soldado de milei")
class Nota(NotaIn):
    class Config:
        orm_mode = True

    id: int
    titulo: str
    cuerpo: str
    created_at: datetime
    mod_at: datetime