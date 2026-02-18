from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from .base import Base


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    serial_number: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    model: Mapped[str] = mapped_column(String(100))
    category: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(default="available")
    specs: Mapped[dict] = mapped_column(JSONB, nullable=True, default={})
    return_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    owner_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    owner: Mapped["User | None"] = relationship(back_populates="devices")
