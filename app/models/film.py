from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base


class Film(Base):
    __tablename__ = "films"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(2000), nullable=True)
    year: Mapped[int] = mapped_column(nullable=False)
    rating: Mapped[float] = mapped_column(nullable=True)

    favorites: Mapped[list["Favorite"]] = relationship(back_populates="film")
    watch_history: Mapped[list["WatchHistory"]] = relationship("film")
