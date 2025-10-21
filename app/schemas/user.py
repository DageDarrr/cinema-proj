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


class UserBase:

    id: int
    username: str
    email: EmailStr

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str):
        if not v or len(v.strip()) < 2:
            raise ValueError("username должен содержать больше двух символов")
        return v.strip()
