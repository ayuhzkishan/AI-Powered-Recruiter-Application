from pydantic import BaseModel, EmailStr, field_validator
import re


class RegisterSchema(BaseModel):
    email: EmailStr
    password: str
    full_name: str

    @field_validator("password")
    @classmethod
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one number")
        return v

    @field_validator("full_name")
    @classmethod
    def sanitize_name(cls, v):
        cleaned = v.strip()
        if len(cleaned) < 2 or len(cleaned) > 100:
            raise ValueError("Name must be between 2 and 100 characters")
        return cleaned


class LoginSchema(BaseModel):
    email: EmailStr
    password: str
