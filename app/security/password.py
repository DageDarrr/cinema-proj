from passlib.context import CryptContext
import bcrypt
import hmac
import hashlib
from app.core.config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def validate_password_strength(password: str) -> str:
    """
    Проверяет надежность пароля:
        Минимум 8 символов
        Как минимум одна заглавная буква
        Как минимум одна строчная буква
        Как минимум одна цифра
    """
    if len(password) < 8:
        raise ValueError("Пароль должен содержать не менее 8 символов")
    if not any(c.isupper() for c in password):
        raise ValueError("Пароль должен содержать хотя бы одну заглавную букву")
    if not any(c.islower() for c in password):
        raise ValueError("Пароль должен содержать хотя бы одну строчную букву")
    if not any(c.isdigit() for c in password):
        raise ValueError("Пароль должен содержать хотя бы одну цифру")
    return password


def get_password_hash(password: str) -> bytes:
    validate_password_strength(password=password)
    
    
    peppered_password = hmac.new(
        settings.PEPPER_SECRET.encode("utf-8"),
        password.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()
    
    
    hashed = bcrypt.hashpw(
        peppered_password.encode("utf-8"),
        bcrypt.gensalt(rounds=settings.BCRYPT_ROUNDS)
    )
    return hashed

def verify_password(input_password: str, hashed_password: bytes) -> bool:
    
    peppered_password = hmac.new(
        settings.PEPPER_SECRET.encode("utf-8"),
        input_password.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()
    
    return bcrypt.checkpw(peppered_password.encode("utf-8"), hashed_password)
