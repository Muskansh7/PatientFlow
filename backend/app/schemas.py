
from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator, ConfigDict
import re


class UserSignup(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: str = Field(max_length=254)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("name")
    @classmethod
    def validate_user_name(cls, value):
        value = value.strip()
        if not re.fullmatch(r"[A-Za-zÀ-ÖØ-öø-ÿ\s'-]+", value):
            raise ValueError("Name contains invalid characters")
        return value

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        value = value.strip().lower()
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", value):
            raise ValueError("Enter a valid email address")
        return value


class UserLogin(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value):
        return value.strip().lower()


class UserResponse(BaseModel):
    id: int
    name: str
    email: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class Gender(str, Enum):
    male = "Male"
    female = "Female"
    transgender = "Transgender"
    non_binary = "Non-binary"
    gender_fluid = "Gender Fluid"
    agender = "Agender"
    other = "Other"
    prefer_not_to_say = "Prefer not to say"


class PatientStatus(str, Enum):
    admitted = "Admitted"
    discharged = "Discharged"


class PatientCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    age: int = Field(..., ge=0, le=120)
    gender: Gender
    ward: str = Field(..., min_length=1)
    department: str = Field(..., min_length=1)
    doctor: str = Field(..., min_length=1)
    admission_date: date
    status: PatientStatus = PatientStatus.admitted

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        value = value.strip()

        if not value:
            raise ValueError("Name cannot be empty")

        if not all(c.isalpha() or c in " -'" for c in value):
            raise ValueError("Name must contain only letters, spaces, hyphens or apostrophes")

        if len(value) < 2:
            raise ValueError("Name must contain at least 2 characters")

        return value

    @field_validator("admission_date")
    @classmethod
    def validate_admission_date(cls, value):
        if value > date.today():
            raise ValueError("Admission date cannot be in the future")

        return value


class PatientUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    age: Optional[int] = Field(None, ge=0, le=120)
    gender: Optional[Gender] = None
    ward: Optional[str] = None
    department: Optional[str] = None
    doctor: Optional[str] = None
    admission_date: Optional[date] = None
    status: Optional[PatientStatus] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        if value is None:
            return value

        value = value.strip()

        if not value:
            raise ValueError("Name cannot be empty")

        if not all(c.isalpha() or c in " -'" for c in value):
            raise ValueError("Name must contain only letters, spaces, hyphens or apostrophes")

        return value

    @field_validator("admission_date")
    @classmethod
    def validate_admission_date(cls, value):
        if value is not None and value > date.today():
            raise ValueError("Admission date cannot be in the future")

        return value


class PatientResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    age: int
    gender: Gender
    ward: str
    department: str
    doctor: str
    admission_date: date
    status: PatientStatus


class PatientListResponse(BaseModel):
    items: list[PatientResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

