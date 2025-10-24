from pydantic import BaseModel, field_validator
from typing import Optional

class CustomerBase(BaseModel):
    name: str
    phone: str
    address: Optional[str]

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        if v is not None:
            if not v.isdigit():
                raise ValueError("Phone number must contain only digits")
            if len(v) != 10:
                raise ValueError("Phone number must be exactly 10 digits long")
        return v

class CustomerCreate(CustomerBase):
    pass

class CustomerResponse(CustomerBase):
    id: int

    class Config:
        from_attributes = True
