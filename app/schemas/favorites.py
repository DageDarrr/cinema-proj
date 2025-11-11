from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class FavoriteBase(BaseModel):

    film_id: int = Field(..., gt=0, description="ID фильма в избраном")
    user_id: int = Field(..., gt=0, description="ID юзера")


class FavoriteCreate(FavoriteBase):
    pass


class FavoriteUpdate(BaseModel):
    film_id: Optional[int] = Field(None, gt=0, description="ID фильма в избраном")


class FavoriteResponse(FavoriteBase):
    id: int = Field(..., description="ID избранного")
    created_at: datetime = Field(..., description="Дата добавления в избраное")

    model_config = ConfigDict(from_attributes=True)
