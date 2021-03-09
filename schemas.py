
from datetime import date
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



    
class UserPost(BaseModel):
    username: str
    password: str

    class Config:
        orm_mode = True
class User(UserPost):
    id: int
    
    class Config:
        orm_mode = True

class Settings(BaseModel):
    authjwt_secret_key: str = "secret_key"

