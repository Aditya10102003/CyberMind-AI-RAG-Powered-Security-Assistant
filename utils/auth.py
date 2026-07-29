from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from datetime import datetime, timedelta

from jose import jwt

from passlib.context import CryptContext

SECRET_KEY = "your_super_secret_key_change_this"

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="login"
)

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def hash_password(password: str):

    return pwd_context.hash(password)


def verify_password(
    plain_password,
    hashed_password
):

    return pwd_context.verify(
        plain_password,
        hashed_password
    )


def create_access_token(data: dict):

    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update(
        {"exp": expire}
    )

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )
def get_current_user(
    token: str = Depends(oauth2_scheme)
):

    credentials_exception = HTTPException(

        status_code=status.HTTP_401_UNAUTHORIZED,

        detail="Could not validate credentials",

        headers={
            "WWW-Authenticate": "Bearer"
        }

    )

    try:

        payload = jwt.decode(

            token,

            SECRET_KEY,

            algorithms=[ALGORITHM]

        )

        username = payload.get("sub")

        if username is None:

            raise credentials_exception

        return username

    except JWTError:

        raise credentials_exception