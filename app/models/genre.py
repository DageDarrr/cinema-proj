from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base
from .association_tables.film_genre import film_genre


class Genre(Base):
    __tablename__ = "genres"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    films: Mapped[list["Film"]] = relationship(
        secondary=film_genre, back_populates="genres"
    )
