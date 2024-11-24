from sqlalchemy import (
    Column,
    String,
    Integer,
    Boolean,
    UniqueConstraint,
    PrimaryKeyConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy_serializer import SerializerMixin

from app.common.models import Common
from utils.database import Base


class Users(Base, Common, SerializerMixin):
    """Models a user table"""
    __tablename__ = "Users"
    serialize_only = ('id', 'email', 'full_name', 'phone', 'address')
    id = Column(Integer, nullable=False, primary_key=True)
    phone = Column(String(15), nullable=False, unique=True)
    full_name = Column(String(225), nullable=False)
    email = Column(String(225), nullable=False, unique=True)
    password = Column(String, nullable=False)
    address = Column(String(225), nullable=False)
    is_active = Column(Boolean, default=False)

    UniqueConstraint("email", name="uq_user_email")
    PrimaryKeyConstraint("id", name="pk_user_id")

    class Config:
        orm_mode = True
