from pydantic import EmailStr

from app.user.models import Users
from utils import store, jwt_token
from utils.exceptions import GenericError


def get_user_or_404(user_id):
    user = Users.query.get(user_id)

    if user and not user.is_deleted:
        return user

    else:
        raise GenericError(
            status_code=404,
            message='User not found'
        )


def get_user_by_email_or_404(email):
    user = Users.query.filter_by(email=email, is_deleted=False).first()
    if not user:
        raise GenericError(
            status_code=404,
            message="User not found",
            errors={'email': f'{email} not found'}
        )

    if not user.is_active:
        raise GenericError(
            status_code=404,
            message='User not active'
        )

    return user


def get_user_by_phone_or_404(phone):
    user = Users.query.filter_by(phone=phone).first()

    if user and not user.is_deleted:
        raise GenericError(
            status_code=404,
            message="Phone number already registered.",
            errors={'phone': f'{phone} already registered.'}
        )
    else:
        return user


def check_existing_user(email):
    user = Users.query.filter_by(email=email).first()
    if user and not user.is_deleted:
        raise GenericError(
            status_code=409,
            message=f'User with email {email} already exists',
        )


def create_user(user):
    hashed_password = jwt_token.get_hashed_password(user.password)
    user_data = user.dict()
    user_data['password'] = hashed_password
    user_data.pop('confirm_password', None)
    new_user = Users(**user_data)
    new_user.is_active = False
    store.session.add(new_user)
    store.session.commit()
    return new_user


def update_user(user, data):
    updated_user = data.dict(exclude_none=True)
    for field, value in updated_user.items():
        setattr(user, field, value)
    store.session.commit()


def verify_user(email: EmailStr):
    user = Users.query.filter_by(email=email).first()
    if user.is_active:
        raise GenericError(
            message='User is already active.',
            status_code=409
        )
    user.is_active = True
    store.session.commit()


def change_password(user, password):
    hashed_password = jwt_token.get_hashed_password(password)
    user.password = hashed_password
    store.session.commit()
