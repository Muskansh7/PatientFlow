from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(50), nullable=False)
    ward = Column(String(100), nullable=False)
    department = Column(String(100), nullable=False)
    doctor = Column(String(100), nullable=False)
    admission_date = Column(Date, nullable=False)
    status = Column(String(20), default="Admitted", nullable=False)

    history = relationship(
        "PatientHistory",
        back_populates="patient",
        cascade="all, delete-orphan"
    )


class PatientHistory(Base):
    __tablename__ = "patient_history"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    action = Column(String(100), nullable=False)
    details = Column(String(500), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    patient = relationship("Patient", back_populates="history")