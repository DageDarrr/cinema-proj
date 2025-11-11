from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base
from .association_tables.film_actor import film_actor
from .association_tables.film_genre import film_genre


class Film(Base):
    __tablename__ = "films"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(2000), nullable=True)
    duration: Mapped[int] = mapped_column(nullable=False)
    year: Mapped[int] = mapped_column(nullable=False)
    rating: Mapped[float] = mapped_column(nullable=True)

    favorites: Mapped[list["Favorite"]] = relationship(back_populates="film")
    watch_history: Mapped[list["WatchHistory"]] = relationship(back_populates="film")
    actors: Mapped[list["Actor"]] = relationship(
        secondary=film_actor, back_populates="films"
    )
    genres: Mapped[list["Genre"]] = relationship(
        secondary=film_genre, back_populates="films"
    )
