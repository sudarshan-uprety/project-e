import random

import redis

from utils.exceptions import GenericError
from utils.variables import REDIS_SERVER


class OTPService:
    def __init__(self, redis_url, expiry_seconds=600):
        self.redis = redis.from_url(redis_url)
        self.expiry_seconds = expiry_seconds

    def generate_otp(self, user_email):
        otp = str(random.randint(1000, 9999))
        key = f"otp:{user_email}"
        self.redis.setex(key, self.expiry_seconds, otp)
        return otp

    def verify_otp(self, user_email, otp):
        key = f"otp:{user_email}"
        stored_otp = self.redis.get(key)
        if stored_otp and stored_otp.decode() == str(otp):
            self.redis.delete(key)
            return True
        raise GenericError(
            message="OTP verification failed. Please try again.",
            status_code=400,
        )


otp = OTPService(redis_url=REDIS_SERVER)
