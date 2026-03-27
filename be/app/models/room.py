from datetime import datetime

from sqlalchemy import DateTime, Enum, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    room_number: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    room_type: Mapped[str] = mapped_column(Enum("single", "double", "suite", "family", name="room_type"), nullable=False, default="single")
    floor: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    price_per_night: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(Enum("available", "occupied", "cleaning", "maintenance", name="room_status"), nullable=False, default="available")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
