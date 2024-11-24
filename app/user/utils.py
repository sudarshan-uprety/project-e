from pydantic import EmailStr

from app.user.queries import verify_user
from utils.otp import otp


def verify_signup_otp(code: str, email: EmailStr) -> None:
    otp.verify_otp(user_email=email, otp=code)
    verify_user(email=email)


def verify_forget_password_otp(code: str, email: EmailStr) -> bool:
    otp.verify_otp(user_email=email, otp=code)
