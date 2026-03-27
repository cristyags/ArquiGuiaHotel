from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class RoomCreate(BaseModel):
    room_number: str
    room_type: str
    floor: int = Field(ge=1)
    price_per_night: float = Field(gt=0)
    capacity: int = Field(ge=1)
    description: str | None = None
    status: str = "available"

    @field_validator("room_number")
    @classmethod
    def validate_room_number(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned.isdigit() or int(cleaned) <= 0:
            raise ValueError("El número de habitación debe ser un entero positivo")
        return str(int(cleaned))


class RoomUpdate(BaseModel):
    room_number: str | None = None
    room_type: str | None = None
    floor: int | None = Field(default=None, ge=1)
    price_per_night: float | None = Field(default=None, gt=0)
    capacity: int | None = Field(default=None, ge=1)
    description: str | None = None
    status: str | None = None

    @field_validator("room_number")
    @classmethod
    def validate_room_number(cls, value: str | None) -> str | None:
        if value is None:
            return value
        cleaned = value.strip()
        if not cleaned.isdigit() or int(cleaned) <= 0:
            raise ValueError("El número de habitación debe ser un entero positivo")
        return str(int(cleaned))


class RoomStatusUpdate(BaseModel):
    status: str


class RoomOut(BaseModel):
    id: int
    room_number: str
    room_type: str
    floor: int
    price_per_night: float
    capacity: int
    description: str | None = None
    status: str
    created_at: datetime | None = None
    updated_at: datetime | None = None
    model_config = ConfigDict(from_attributes=True)
