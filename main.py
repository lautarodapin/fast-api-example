from typing import List

from fastapi import Depends, FastAPI, HTTPException, Request, status, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from starlette.status import HTTP_200_OK

import models, schemas
from settings import Settings
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# Dependency
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

@app.on_event("shutdown")
def on_shutdown(db: Session = Depends(get_db)):
    pass


@AuthJWT.load_config
def jwt_load_config():
    return Settings()


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
)


@app.get("/")
def main():
    return RedirectResponse(url="/docs/")
    
@app.post('/login', status_code=status.HTTP_200_OK, tags=["auth"])
def login(user: schemas.UserIn, Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    _user = db.query(models.User).filter(models.User.username == user.username).first()
    if _user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"El usuario {user.username} no esta registrado")
    
    if not _user.check_password(user.password):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Se ingreso la contraseña incorrecta para el usuario {user.username}")

    access_token = Authorize.create_access_token(subject=user.username)
    refresh_token = Authorize.create_refresh_token(subject=user.username)
    Authorize.set_access_cookies(access_token)
    Authorize.set_refresh_cookies(refresh_token)
    return {"msg":"Successfully login"}
    # return {"access_token": access_token}


@app.post('/refresh', status_code=status.HTTP_200_OK, tags=["auth"])
def refresh(Authorize: AuthJWT = Depends()):
    Authorize.jwt_refresh_token_required()

    current_user = Authorize.get_jwt_subject()
    new_access_token = Authorize.create_access_token(subject=current_user)
    Authorize.set_access_cookies(new_access_token)
    return {"msg":"The token has been refresh"}


@app.delete('/logout', status_code=status.HTTP_200_OK, tags=["auth"])
def logout(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()

    Authorize.unset_jwt_cookies()
    return {"msg":"Successfully logout"}


@app.get('/user', response_model=List[schemas.User], status_code=HTTP_200_OK, tags=["users"])
def user(Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    Authorize.jwt_required()
    users = db.query(models.User).all()
    return users


@app.post("/user", response_model=schemas.User, status_code=status.HTTP_201_CREATED, tags=["users"])
def create_user(user: schemas.UserIn, db: Session = Depends(get_db)):
    data = models.User(**user.dict())
    data.set_password(data.password)
    db.add(data)
    db.commit()
    return data


@app.delete("/user/{pk}", status_code=status.HTTP_200_OK, tags=["users"])
async def delete_user(pk: int, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    user = db.query(models.User).get(pk)
    db.delete(user)
    db.commit()
    return dict(msg=f"El usuario {user.username} fue borrado correctamente")



@app.get("/user/get-current/", response_model=schemas.User, status_code=status.HTTP_200_OK, tags=["users"])
def get_current_user(auth: AuthJWT = Depends(), db: Session = Depends(get_db)):
    auth.jwt_required()
    username: str = auth.get_jwt_subject()
    user = db.query(models.User).filter(models.User.username == username).first()
    return user


@app.get("/records/", response_model=List[schemas.Record], status_code=status.HTTP_200_OK, tags=["records"])
def show_records(db: Session = Depends(get_db)):
    records = db.query(models.Record).all()
    return records


@app.post("/records/", response_model=schemas.Record, status_code=status.HTTP_201_CREATED, tags=["records"])
def post_record(record: schemas.PostRecord, db: Session = Depends(get_db)):
    data = models.Record(**record.dict())
    db.add(data)
    db.commit()
    return data


@app.get("/records/{pk}/", response_model=schemas.Record, status_code=status.HTTP_200_OK, tags=["records"])
def get_record(pk: int, db: Session = Depends(get_db)):
    record = db.query(models.Record).filter(models.Record.id == pk).first()
    return record


@app.delete("/records/{pk}/", status_code=status.HTTP_200_OK, tags=["records"])
def delete_record(pk: int, db: Session = Depends(get_db)):
    record = db.query(models.Record).get(pk)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Record {pk} not found")
    db.delete(record)
    db.commit()
    return {"msg": f"Record {pk} deleted successfully!"}


""" NOTAS """
@app.get("/notas", response_model=List[schemas.Nota], status_code=status.HTTP_200_OK, tags=["notas"])
def notas(db: Session = Depends(get_db)):
    notas = db.query(models.Nota).all()
    return notas

@app.post("/notas", response_model=schemas.Nota, status_code=status.HTTP_201_CREATED, tags=["notas"])
def create_nota(nota: schemas.NotaIn, db: Session = Depends(get_db), auth: AuthJWT = Depends()):
    auth.jwt_required()
    nota = models.Nota(**nota.dict())
    db.add(nota)
    db.commit()
    return nota

@app.delete("/notas/{pk}", status_code=status.HTTP_200_OK, tags=["notas"])
def delete_nota(pk: int, db: Session = Depends(get_db), auth: AuthJWT = Depends()):
    auth.jwt_required()
    nota = db.query(models.Nota).get(pk)
    db.delete(nota)
    db.commit()
    return dict(msg=f"La nota {nota.titulo} fue borrada correctamente")