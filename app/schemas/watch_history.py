from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class WatchHistoryBase(BaseModel):

    user_id: int = Field(..., gt=0, description="ID пользователя")
    film_id: int = Field(..., gt=0, description="ID фильма в истории")
    watch_duration: int = Field(
        ..., ge=0, description="Сколько времени просмотренно в секундах"
    )


class WatchHistoryCreate(WatchHistoryBase):
    pass


class WatchHistoryUpdate(BaseModel):
    watch_duration: Optional[int] = Field(
        None, ge=0, description="Сколько времени просмотрено в секундах"
    )


class WatchHistoryResponse(WatchHistoryBase):
    id: int = Field(..., description="ID истории просмотра")
    watched_at: datetime = Field(..., description="Когда просмотрено")

    model_config = ConfigDict(from_attributes=True)
