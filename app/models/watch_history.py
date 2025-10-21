from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base
from datetime import datetime, timezone





class WatchHistory(Base):
    __tablename__ = 'watch_history'

    id : Mapped[int] = mapped_column(primary_key=True)
    user_id : Mapped[int] = mapped_column(ForeignKey("users.id"))
    film_id : Mapped[int] = mapped_column(ForeignKey("films.id"))
    watched_at : Mapped[datetime] = mapped_column(default=lambda : datetime.now(timezone.utc))
    watch_duration : Mapped[int] = mapped_column(default=0)

    user: Mapped["User"] = relationship(back_populates="watch_history")
    film: Mapped["Film"] = relationship(back_populates="watch_history")


    