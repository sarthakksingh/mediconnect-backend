from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Dict, Optional


# ─── Auth ────────────────────────────────────────────────

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    password: str
    role: str = "PATIENT"  # PATIENT / DOCTOR / ADMIN


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    name: str
    role: str


# ─── Appointments ────────────────────────────────────────

class AppointmentCreate(BaseModel):
    patient_id: int
    doctor_id: int
    date_time: datetime
    reason: Optional[str] = None


class AppointmentReschedule(BaseModel):
    appointment_id: int
    new_date_time: datetime


# ─── Doctor ──────────────────────────────────────────────

class AvailabilitySet(BaseModel):
    doctor_id: int
    availability: Dict


# ─── Reports ─────────────────────────────────────────────

class ReportReady(BaseModel):
    appointment_id: int
    report_ready_date: datetime