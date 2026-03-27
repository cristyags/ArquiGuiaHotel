from pydantic import BaseModel, ConfigDict, EmailStr


class GuestCreate(BaseModel):
    full_name: str
    email: EmailStr
    phone: str | None = None
    document_id: str | None = None


class GuestOut(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    phone: str | None = None
    document_id: str | None = None
    model_config = ConfigDict(from_attributes=True)
