from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, Table, TIMESTAMP
from sqlalchemy.orm import relationship
from src.database import Base, engine


class User(Base):
    __tablename__ = "users"

    id = Column(String(50), primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    password = Column(String(50))
    hashed_password = Column(String(150), nullable=False)
    created_at = Column(TIMESTAMP, index=True)

    board = relationship("Board", back_populates="user")
    permissions = relationship("Permission", secondary="user_permissions")


# User.metadata.create_all(engine)


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(50))
    codename = Column(String(50))

    users = relationship("User", secondary="user_permissions")


# Permission.metadata.create_all(engine)


user_permissions = Table(
    "user_permissions",
    Base.metadata,
    Column("id", String(50), primary_key=True, index=True),
    Column("user_id", String(50), ForeignKey("users.id")),
    Column("permission_id", String(50), ForeignKey("permissions.id")),
)
