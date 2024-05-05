from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session
from src import schemas, models
from src.database import get_db
from utils.auth import get_user, authenticate_user, create_access_token, get_password_hash, has_permission
import datetime
import dotenv, os
import uuid

dotenv.load_dotenv(os.path.join(".env"))


router = APIRouter(
    prefix="/users",
    tags=["User"],
    responses={404: {"description": "Not found"}},
)


@router.get("")
def get_users(db: Session = Depends(get_db), user=Depends(get_user)):
    print(user, "fdsfsd")
    if not has_permission(user, "admin"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    users = db.query(models.User).all()
    db.close()
    return users


# login user
@router.post("/login", response_model=schemas.Token)
async def login_for_access_token(
    user_credentials: schemas.LoginUser,
    db: Session = Depends(get_db),
):
    user = authenticate_user(db, user_credentials.username, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = datetime.timedelta(minutes=int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES")))
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


# create user
@router.post("")
async def create_user(data: schemas.User, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter_by(username=data.username).first()
    if existing_user:
        raise HTTPException(400, "کاربر با این نام کاربری وجود دارد")
    new_user = models.User(
        id=str(uuid.uuid4()),
        username=data.username,
        password=data.password,
        hashed_password=get_password_hash(data.password),
        created_at=datetime.datetime.utcnow(),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    db.close()
    return new_user


# update user
@router.patch("/{user_id}")
async def update_user(user_id: int, user_data: schemas.UserUpdate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    for key, value in user_data:
        if hasattr(user_data, key) and value is not None and value:
            if key == "password":
                key = "hashed_password"
                value = get_password_hash(value)
            elif key == "is_admin" or key == "is_employer" or key == "is_near" or key == "is_active":
                value = int(value)
            setattr(user, key, value)
    db.commit()
    db.close()
    return {"message": "User updated successfully"}


@router.delete("/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).get(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    projects = db.query(models.ProjectAssignee).filter(user_id == user.id).all()
    for project in projects:
        db.delete(project)

    db.delete(user)
    db.commit()
    db.close()

    return {"message": "User deleted successfully"}
