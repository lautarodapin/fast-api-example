from typing import List

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException

import models, schemas
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
    return schemas.Settings()

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
def login(user: schemas.UserPost, Authorize: AuthJWT = Depends()):
    if user.username != "test" or user.password != "test":
        raise HTTPException(status_code=401,detail="Bad username or password")

    # subject identifier for who this token is for example id or username from database
    access_token = Authorize.create_access_token(subject=user.username)
    return {"access_token": access_token}

# protect endpoint with function jwt_required(), which requires
# a valid access token in the request headers to access.
@app.get('/user')
def user(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()

    current_user = Authorize.get_jwt_subject()
    return {"user": current_user}

@app.post("/user", response_model=schemas.User)
def create_user(user: schemas.UserPost, db: Session = Depends(get_db)):
    data = models.User(**user.dict())
    db.add(data)
    db.commit()
    return data

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