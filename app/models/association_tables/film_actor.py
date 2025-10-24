from sqlalchemy import Table, Column, ForeignKey
from app.models.base import Base


""""Асоциативная таблица для many to many связи, у каждого актера много фильмов

У каждого актера много фильмов в которых он снимался,

У каждого фильма много актеров

"""


film_actor = Table(
    'film_actor',
    Base.metadata,
    Column('film_id', ForeignKey('films.id'), primary_key=True),
    Column('actor_id', ForeignKey('actors.id'), primary_key=True),
    
)