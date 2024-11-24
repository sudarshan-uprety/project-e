from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator

from app.user.queries import get_user_by_phone_or_404, check_existing_user
from utils import exceptions


class UserRegister(BaseModel):
    email: EmailStr
    full_name: str
    phone: str
    address: str
    password: str
    confirm_password: str

    @field_validator('password')
    def validate_password(cls, value):
        if len(value) < 8:
            raise exceptions.GenericError(
                message='Password must be at least 8 characters long',
                status_code=400
            )
        return value

    @field_validator('confirm_password')
    def passwords_match(cls, value, values):
        if value != values.data.get('password'):
            raise exceptions.GenericError(
                message='Password and confirm_password must be same must match',
                status_code=400
            )
        return value

    @field_validator('phone')
    def validate_phone(cls, value):
        if len(value) < 10:
            raise exceptions.GenericError(
                message='Phone must be at least 10 characters long',
                status_code=400
            )
        phone = get_user_by_phone_or_404(phone=value)
        return value

    @field_validator('email')
    def validate_email(cls, value):
        check_existing_user(value)
        return value

    class Config:
        from_attributes = True


class UserRegisterResponse(BaseModel):
    email: EmailStr
    full_name: str
    phone: str
    address: str

    class Config:
        from_attributes = True


class OTPVerification(BaseModel):
    email: EmailStr
    otp: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    user: UserRegisterResponse

    class Config:
        from_attributes = True


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str


class UserDetails(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    created_at: datetime
    address: str
    phone: str

    class Config:
        from_attributes = True


class EmailSchema(BaseModel):
    email: EmailStr


class ForgetPasswordRequest(BaseModel):
    email: EmailStr
    password: str
    confirm_password: str
    otp: str

    @field_validator('password')
    def validate_password(cls, value):
        if len(value) < 8:
            raise exceptions.GenericError(
                message='Password must be at least 8 characters long',
                status_code=400
            )
        return value

    @field_validator('confirm_password')
    def passwords_match(cls, value, values):
        if value != values.data.get('password'):
            raise exceptions.GenericError(
                message='Password and confirm_password must be same must match',
                status_code=400
            )
        return value

    @field_validator('otp')
    def validate_otp(cls, value):
        if len(value) < 4 or len(value) > 4:
            raise exceptions.GenericError(
                message='OTP must be 4 characters long',
                status_code=400
            )
        return value


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str

    @field_validator('new_password')
    def validate_password(cls, value):
        if len(value) < 8:
            raise exceptions.GenericError(
                message='Password must be at least 8 characters long',
                status_code=400
            )
        return value

    @field_validator('confirm_password')
    def passwords_match(cls, value, values):
        if value != values.data.get('new_password'):
            raise exceptions.GenericError(
                message='Password and confirm_password must be same must match',
                status_code=400
            )
        return value


class TokenPayload(BaseModel):
    sub: str
    exp: int


class UpdateUserDetails(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

    class Config:
        from_attributes = True
