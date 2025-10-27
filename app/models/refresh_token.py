from sqlalchemy import String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base
from datetime import datetime
from sqlalchemy.sql import func



class RefreshToken(Base):
    __tablename__ = 'refresh_tokens'

    id : Mapped[int] = mapped_column(primary_key=True)
    user_id : Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    token : Mapped[str] = mapped_column(String(512), unique=True, nullable=False)
    expires_at : Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    is_revoked : Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at : Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

    user : Mapped["User"] = relationship(back_populates="refresh_tokens")