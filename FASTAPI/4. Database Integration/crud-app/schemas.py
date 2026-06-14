from pydantic import BaseModel, EmailStr, field_validator
# from typing import Optional

class EmployeeBase(BaseModel):
    name: str
    email: EmailStr

    # Production-ready custom validator: Ensure name has no digits/numbers
    @field_validator('name')
    @classmethod
    def validate_name(cls, value: str) -> str:
        stripped_value = value.strip()
        if any(char.isdigit() for char in stripped_value):
            raise ValueError("Name must not contain any numbers")
        return stripped_value

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeUpdate(EmployeeBase):
    pass

class EmployeeOut(EmployeeBase):
    id: int

    # Config class to allow Pydantic to read SQLAlchemy ORM objects
    class Config:
        from_attributes = True # Modern Pydantic V2 replacement for orm_mode = True
        orm_mode = True        # Backwards compatibility fallback for older Pydantic V1 setups