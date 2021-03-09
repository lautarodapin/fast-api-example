from typing import List

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException

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


@app.post('/login')
def login(user: schemas.UserIn, Authorize: AuthJWT = Depends()):
    # if user.username != "test" or user.password != "test":
    #     raise HTTPException(status_code=401,detail="Bad username or password")

    access_token = Authorize.create_access_token(subject=user.username)
    refresh_token = Authorize.create_refresh_token(subject=user.username)
    Authorize.set_access_cookies(access_token)
    Authorize.set_refresh_cookies(refresh_token)
    return {"msg":"Successfully login"}
    # return {"access_token": access_token}


@app.post('/refresh')
def refresh(Authorize: AuthJWT = Depends()):
    Authorize.jwt_refresh_token_required()

    current_user = Authorize.get_jwt_subject()
    new_access_token = Authorize.create_access_token(subject=current_user)
    Authorize.set_access_cookies(new_access_token)
    return {"msg":"The token has been refresh"}


@app.delete('/logout')
def logout(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()

    Authorize.unset_jwt_cookies()
    return {"msg":"Successfully logout"}


@app.get('/user', response_model=List[schemas.User])
def user(Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    Authorize.jwt_required()
    users = db.query(models.User).all()
    return users


@app.post("/user", response_model=schemas.User)
def create_user(user: schemas.UserIn, db: Session = Depends(get_db)):
    data = models.User(**user.dict())
    db.add(data)
    db.commit()
    return data


@app.get("/user/get-current/", response_model=schemas.User)
def get_current_user(auth: AuthJWT = Depends(), db: Session = Depends(get_db)):
    auth.jwt_required()
    username: str = auth.get_jwt_subject()
    user = db.query(models.User).filter(models.User.username == username).first()
    return user


@app.get("/records/", response_model=List[schemas.Record])
def show_records(db: Session = Depends(get_db)):
    records = db.query(models.Record).all()
    return records


@app.post("/records/", response_model=schemas.Record)
def post_record(record: schemas.PostRecord, db: Session = Depends(get_db)):
    data = models.Record(**record.dict())
    db.add(data)
    db.commit()
    return data


@app.get("/records/{pk}/", response_model=schemas.Record)
def get_record(pk: int, db: Session = Depends(get_db)):
    record = db.query(models.Record).filter(models.Record.id == pk).first()
    return record


@app.delete("/records/{pk}/")
def delete_record(pk: int, db: Session = Depends(get_db)):
    record = db.query(models.Record).get(pk)
    if not record:
        raise HTTPException(status_code=404, detail=f"Record {pk} not found")
    db.delete(record)
    db.commit()
    return {"msg": f"Record {pk} deleted successfully!"}