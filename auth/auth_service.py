"""
Сервис аутентификации и авторизации (JWT + bcrypt).
Соответствует требованиям ФСТЭК России по идентификации и аутентификации.
"""

from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from server.storage.models import User
from server.logging_service.logger import get_logger
from server.config.settings import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

logger = get_logger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    logger.info(f"Выдан токен для пользователя: {data.get('sub')}")
    return token


def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as exc:
        logger.warning(f"Ошибка декодирования токена: {exc}")
        return None


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    user = db.query(User).filter(User.username == username).first()
    if not user:
        logger.warning(f"Пользователь не найден: {username}")
        return None
    if not verify_password(password, user.hashed_password):
        logger.warning(f"Неверный пароль для пользователя: {username}")
        return None
    if not user.is_active:
        logger.warning(f"Пользователь заблокирован: {username}")
        return None
    logger.info(f"Успешная аутентификация: {username}")
    return user


def create_default_admin(db: Session):
    existing = db.query(User).filter(User.username == "admin").first()
    if not existing:
        admin = User(
            username="admin",
            hashed_password=hash_password("Admin1234!"),
            role="admin",
        )
        db.add(admin)
        db.commit()
        logger.info("Создан пользователь по умолчанию: admin")
