from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    hashed_password: Mapped[bytes] = mapped_column(nullable=False)

    favorites: Mapped[list["Favorite"]] = relationship(back_populates="user")
    watch_history: Mapped[list["WatchHistory"]] = relationship("user")
