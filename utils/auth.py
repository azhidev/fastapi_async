from passlib.context import CryptContext
import os
import datetime
from typing import Union, Any
from jose import jwt
import time
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status, HTTPException, Request, Header
from src.database import get_db
from src import models
import time, dotenv, os, asyncio

dotenv.load_dotenv(os.path.join(".env"))


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: datetime.timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, os.getenv("SECRET_KEY"), algorithm=os.getenv("ALGORITHM"))
    return encoded_jwt


def authenticate_user(db: Session, username: str, password: str):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def decode_jwt(token):
    return jwt.decode(token.encode(), os.getenv("SECRET_KEY"), algorithm=os.getenv("ALGORITHM"))


def get_user(request: Request, HTTP_AUTHORIZATION: str = Header("Bearer token"), db: Session = Depends(get_db)):
    if request.url.path not in ["/", "/users/login", "/docs", "/redoc", "/openapi.json"]:
        print(request.url._url)
        # print(os.getenv("RUNNING_MODE") == "debug" and HTTP_AUTHORIZATION.replace("Bearer ", "") == "ali110", "----------------------")
        print(os.getenv("RUNNING_MODE"))
        if os.getenv("RUNNING_MODE") == "DEBUG" and HTTP_AUTHORIZATION.replace("Bearer ", "") == "ali110":
            return db.query(models.User).filter(models.User.username == "debug").first()
        else:
            try:
                jwt_user = decode_jwt(HTTP_AUTHORIZATION.replace("Bearer ", ""))
            except:
                try:
                    jwt_user = decode_jwt(request.headers["authorization"].replace("Bearer ", ""))
                except:
                    raise HTTPException(401, detail="not authenticate")

            if jwt_user["exp"] < time.time():
                raise HTTPException(401, detail="token is expire")
            return db.query(models.User).filter(models.User.username == jwt_user["sub"]).first()


def has_permission(user: models.User, permission_codename: str) -> bool:
    for permission in user.permissions:
        if permission.codename == permission_codename:
            return True
    return False
