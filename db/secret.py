from jose import JWTError, jwt
from passlib.context import CryptContext
import datetime


SECRET_KEY = "228df6cae9ff2b003a4d9643f5a436fb40b8f94269292e2e010e71c1949ed30d"  # TODO regenerate
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def encode_data(data, secret_key: str = SECRET_KEY, algorithm: str = ALGORITHM):
    return jwt.encode(data, secret_key, algorithm=algorithm)


def generate_token(email: str, expire_time: int = ACCESS_TOKEN_EXPIRE_MINUTES):
    exp = datetime.datetime.utcnow() + datetime.timedelta(minutes=expire_time)
    user_dict = {"email": email,
                 "expiration_date": exp.isoformat()}
    return encode_data(user_dict)


def decode_token(token, secret_key: str = SECRET_KEY, algorithm: str = ALGORITHM):
    try:
        decode_data = jwt.decode(token, secret_key, algorithm)
    except JWTError:
        decode_data = None
    return decode_data
