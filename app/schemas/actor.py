from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.film import FilmResponse



class ActorBase(BaseModel):
    
    
    name : str = Field(..., min_length= 1 , max_length=50, description='Имя актера')
    surname : str = Field(..., min_length=1, max_length=50, description='Фамилия актера')
    age : Optional[int] = Field(None, ge=0, le=130, description='Возраст актера')


class ActorCreate(ActorBase):
    pass


class ActorUpdate(BaseModel):
    
    name : Optional[str] = Field(None, min_length= 1 , max_length=50, description='Имя актера')
    surname : Optional[str] = Field(None, min_length= 1, max_length=50, description='Фамилия актера')
    age : Optional[int] = Field(None, ge=0, le=130, description='Возраст актера')



class ActorResponse(ActorBase):

    id : int = Field(..., description='ID Актера')

    model_config = ConfigDict(from_attributes=True)


class ActorWithFilmsResponse(ActorResponse):
    films: list[FilmResponse] = Field([], description="Фильмы актера")


class ActorListResponse(BaseModel):
    items: list[ActorResponse] = Field(..., description="Список актеров")
    total: int = Field(..., description="Общее количество")

    model_config = ConfigDict(from_attributes=True)
