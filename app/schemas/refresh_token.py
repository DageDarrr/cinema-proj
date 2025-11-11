from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class RefreshTokenCreate(BaseModel):
    user_id: int = Field(..., gt=0, description="ID юзера")
    token: str = Field(
        ...,
        min_length=10,
        max_length=512,
        description="refresh token юзера от 10 до 512 симоволов",
    )
    expires_at: datetime = Field(..., description="Время истечения токена")


class RefreshTokenUpdate(BaseModel):
    is_revoked: bool = Field(..., description="Флаг отозван ли токен")


class RefreshTokenResponse(BaseModel):
    id: int = Field(..., gt=0, description="ID refresh токена")
    user_id: int = Field(..., description="ID юезера")
    token: str = Field(
        ...,
        min_length=10,
        max_length=512,
        description="refresh token минимальная длинна 10, 512 максмаимальная",
    )
    expires_at: datetime = Field(..., description="Время истечения токена")
    is_revoked: bool = Field(..., description="Флаг отозван ли токен")
    created_at: datetime = Field(..., description="Время создания токена")
