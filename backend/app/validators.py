
from datetime import date
import re


def validate_name(name: str) -> str:
    name = name.strip()

    if len(name) < 2 or len(name) > 100:
        raise ValueError("Name must be between 2 and 100 characters")

    if not re.fullmatch(r"[A-Za-zÀ-ÖØ-öø-ÿ\s'-]+", name):
        raise ValueError("Name contains invalid characters")

    return name


def validate_age(age: int) -> int:
    if not isinstance(age, int) or isinstance(age, bool):
        raise ValueError("Age must be an integer")

    if age < 0 or age > 120:
        raise ValueError("Age must be between 0 and 120")

    return age


def validate_admission_date(admission_date: date) -> date:
    if admission_date > date.today():
        raise ValueError("Admission date cannot be in the future")

    return admission_date


def validate_required_text(value: str, field_name: str) -> str:
    value = value.strip()

    if not value:
        raise ValueError(f"{field_name} cannot be empty")

    return value
