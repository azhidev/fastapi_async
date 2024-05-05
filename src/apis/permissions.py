from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session
from src import schemas, models
from src.database import get_db
from utils.auth import get_user, authenticate_user, create_access_token, get_password_hash
from datetime import datetime

router = APIRouter(
    prefix="/permissions",
    tags=["Permission"],
    responses={404: {"description": "Not found"}},
)


@router.post("/permissions", status_code=201)
def create_permission(permission: schemas.PermissionCreate, db: Session = Depends(get_db)):
    db_permission = schemas.Permission(name=permission.name, codename=permission.codename)
    db.add(db_permission)
    db.commit()
    db.refresh(db_permission)
    return db_permission


@router.get("/permissions/{permission_id}", response_model=schemas.Permission)
def get_permission(permission_id: int, db: Session = Depends(get_db)):
    db_permission = db.query(schemas.Permission).filter(schemas.Permission.id == permission_id).first()
    if not db_permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    return db_permission


@router.put("/permissions/{permission_id}", response_model=schemas.Permission)
def update_permission(permission_id: int, permission: schemas.PermissionUpdate, db: Session = Depends(get_db)):
    db_permission = db.query(schemas.Permission).filter(schemas.Permission.id == permission_id).first()
    if not db_permission:
        raise HTTPException(status_code=404, detail="Permission not found")

    db_permission.name = permission.name
    db_permission.codename = permission.codename
    db.commit()
    db.refresh(db_permission)
    return db_permission


@router.delete("/permissions/{permission_id}", status_code=204)
def delete_permission(permission_id: int, db: Session = Depends(get_db)):
    db_permission = db.query(schemas.Permission).filter(schemas.Permission.id == permission_id).first()
    if not db_permission:
        raise HTTPException(status_code=404, detail="Permission not found")

    db.delete(db_permission)
    db.commit()
