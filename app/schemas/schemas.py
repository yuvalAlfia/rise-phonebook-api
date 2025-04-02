from pydantic import BaseModel
from typing import Optional

class ContactBase(BaseModel):
    first_name: str
    last_name: str
    phone: str
    address: str | None = None

class ContactCreate(ContactBase):
    pass

class ContactUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

class ContactOut(ContactBase):
    id: int

    model_config = {
        "from_attributes": True
    }
