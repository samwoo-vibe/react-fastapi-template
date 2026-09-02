from datetime import datetime

from sqlalchemy import DateTime, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Visit(Base):
    __tablename__ = "portal_visits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    visited_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
