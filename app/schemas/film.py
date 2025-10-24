from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class FilmBase(BaseModel):

    title: str = Field(..., min_length=1, max_length=255, description="Название фильма")
    description: Optional[str] = Field(
        None, max_length=2000, description="Описание фильма"
    )
    duration : int = Field(..., gt=0, description="Длительность фильма в секундах")

    year: int = Field(
        ..., gt=1900, le=datetime.now().year, description="Год выпуска фильма"
    )
    rating: float = Field(None, ge=0, le=10, description="Рейтинг фильма")


class FilmCreate(FilmBase):
    pass


class FilmUpdate(BaseModel):

    title: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Название фильма"
    )
    description: Optional[str] = Field(
        None, max_length=2000, description="Описание фильма"
    )
    duration: Optional[int] = Field(None, gt=0, description="Длительность фильма")
    year: Optional[int] = Field(None, gt=1900, le=datetime.now().year, description="Год выпуска фильма")
    rating: Optional[float] = Field(None, ge=0, le=10, description="Рейтинг фильма")


class FilmResponse(FilmBase):

    id: int = Field(..., description="ID фильма")
    created_at: Optional[datetime] = Field(None, description="Дата создания")

    model_config = ConfigDict(from_attributes=True)
