from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta, timezone
import jwt
import schemas
from jwt import PyJWTError
from config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_access_token(token: str, credentials_exception):

    try: 
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: int = payload.get("user_id")

        if id is None:
            raise credentials_exception
    
        token_data = schemas.TokenData(id=id)
    except PyJWTError:
        raise credentials_exception
    except AssertionError as e:
        print(e)
    
    return token_data.id
