from sqlalchemy import Table, Column, Integer, ForeignKey
from ..base import Base


film_genre = Table(
    "film_genre",
    Base.metadata,
    Column("film_id", Integer, ForeignKey("films.id"), primary_key=True),
    Column("genre_id", Integer, ForeignKey("genres.id"), primary_key=True),
)
