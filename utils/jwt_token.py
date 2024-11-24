from datetime import datetime, timedelta
from typing import Union, Any

from fastapi import status
from jose import jwt
from passlib.context import CryptContext

from utils import exceptions
from utils.variables import (ACCESS_TOKEN_EXPIRE_MINUTES, JWT_REFRESH_SECRET_KEY, ALGORITHM, JWT_SECRET_KEY,
                             REFRESH_TOKEN_EXPIRE_MINUTES)

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_hashed_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(password: str, hashed_pass: str) -> None:
    if not password_context.verify(password, hashed_pass):
        raise exceptions.GenericError(
            message="Invalid password",
            status_code=status.HTTP_401_UNAUTHORIZED
        )


def compare_passwords(new_password: str, old_hashed_password: str) -> None:
    if password_context.verify(new_password, old_hashed_password):
        raise exceptions.GenericError(
            message="New password cannot be current password.",
            status_code=status.HTTP_400_BAD_REQUEST
        )


def create_access_token(subject: Union[str, Any], expires_delta: int = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))

    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, ALGORITHM)
    return encoded_jwt


def create_refresh_token(subject: Union[str, Any], expires_delta: int = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=int(REFRESH_TOKEN_EXPIRE_MINUTES))

    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, JWT_REFRESH_SECRET_KEY, ALGORITHM)
    return encoded_jwt


def verify_refresh_token(refresh_token: str) -> str:
    payload = jwt.decode(refresh_token, JWT_REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
    return payload.get('sub')
