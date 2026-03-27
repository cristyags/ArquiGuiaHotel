from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ReservationCreate(BaseModel):
    room_id: int = Field(gt=0)
    guest_id: int = Field(gt=0)
    check_in_date: date
    check_out_date: date
    notes: str | None = None

    @model_validator(mode="after")
    def validate_dates(self):
        if self.check_out_date <= self.check_in_date:
            raise ValueError("La fecha de salida debe ser posterior a la fecha de ingreso")
        return self


class ReservationUpdate(BaseModel):
    room_id: int = Field(gt=0)
    guest_id: int = Field(gt=0)
    check_in_date: date
    check_out_date: date
    notes: str | None = None

    @model_validator(mode="after")
    def validate_dates(self):
        if self.check_out_date <= self.check_in_date:
            raise ValueError("La fecha de salida debe ser posterior a la fecha de ingreso")
        return self


class ReservationStatusUpdate(BaseModel):
    status: Literal["checked_in", "checked_out", "cancelled"]


class ReservationOut(BaseModel):
    id: int
    room_id: int
    guest_id: int
    staff_id: int
    check_in_date: date
    check_out_date: date
    nightly_rate: float
    total_amount: float
    status: str
    notes: str | None = None
    created_at: datetime | None = None
    model_config = ConfigDict(from_attributes=True)
