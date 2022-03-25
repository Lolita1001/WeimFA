from typing import Any
import datetime

from jose import JWTError, jwt
from passlib.context import CryptContext


class SecurityRepository:
    def __init__(self):
        self.SECRET_KEY = "228df6cae9ff2b003a4d9643f5a436fb40b8f94269292e2e010e71c1949ed30d"  # TODO regenerate
        self.ALGORITHM = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES = 30
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password):
        return self.pwd_context.hash(password)

    def encode_data(self, data):
        return jwt.encode(data, self.SECRET_KEY, algorithm=self.ALGORITHM)

    def generate_token(self, data: Any):
        exp = datetime.datetime.utcnow() + datetime.timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        data_dict = {"data": data,
                     "expiration_date": exp.isoformat()}
        return self.encode_data(data_dict)

    def decode_token(self, token):
        try:
            decode_data = jwt.decode(token, self.SECRET_KEY, self.ALGORITHM)
        except JWTError:
            decode_data = None
        return decode_data

