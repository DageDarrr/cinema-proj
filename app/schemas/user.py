from datetime import datetime
from typing import Optional
from pydantic import (
    BaseModel,
    Field,
    EmailStr,
    ConfigDict,
    field_validator,
    model_validator,
)
from app.security.password import validate_password_strength


# Доделать схему валидации юзера , но сначала сделать JWT


class UserBase(BaseModel):

    username: str
    email: EmailStr

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str):
        if not v or len(v.strip()) < 2:
            raise ValueError("username должен содержать больше двух символов")

        if len(v) > 50:
            raise ValueError("username не должен содержать более 50 символов")

        return v.strip()

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str):
        if len(v) > 255:
            raise ValueError("email не должен содержать более 255 символов")

        return v.strip().lower()


class UserCreate(UserBase):

    password: str = Field(..., min_length=8)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str):
        return validate_password_strength(v)


class UserUpdate(BaseModel):

    username: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str):
        if v is None:
            return v

        if not v or len(v.strip()) < 2:
            raise ValueError("username должен содержать больше двух символов")

        if len(v.strip()) > 50:
            raise ValueError("username не должен содержать более 50 символов")
        return v.strip()


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    username: str
    password: str


class UserChangePassword(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str):
        return validate_password_strength(v)
