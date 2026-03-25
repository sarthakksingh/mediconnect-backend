from pydantic import BaseModel, EmailStr
from datetime import datetime, date
from typing import Dict, Optional, List


# ─── Auth ────────────────────────────────────────────────

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    password: str
    doctor_code: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    name: str
    role: str


# ─── User / Profile ──────────────────────────────────────

class UserProfileOut(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str]
    role: str
    blood_group: Optional[str]
    date_of_birth: Optional[date]
    gender: Optional[str]

    class Config:
        from_attributes = True


class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    blood_group: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None


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


class DoctorAppointmentOut(BaseModel):
    appointment_id: int
    patient_name: str
    patient_email: str
    patient_phone: Optional[str]
    date_time: datetime
    reason: Optional[str]
    status: str


# ─── Reports ─────────────────────────────────────────────

class ReportReady(BaseModel):
    appointment_id: int
    report_ready_date: datetime


# ─── Firebase ────────────────────────────────────────────

class FirebaseLoginRequest(BaseModel):
    id_token: str


# ─── Medicines ───────────────────────────────────────────

class MedicineCreate(BaseModel):
    name: str
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    notes: Optional[str] = None


class MedicineOut(BaseModel):
    id: int
    name: str
    dosage: Optional[str]
    frequency: Optional[str]
    start_date: Optional[date]
    end_date: Optional[date]
    is_active: bool
    notes: Optional[str]

    class Config:
        from_attributes = True


class MedicineUpdate(BaseModel):
    name: Optional[str] = None
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    end_date: Optional[date] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None


# ─── Health Score ─────────────────────────────────────────

class HealthScoreOut(BaseModel):
    score: int                    # 0–100
    completion_rate: float        # % appointments completed
    adherence_score: float        # % active medicines (proxy for adherence)
    streak_score: float           # bonus for having upcoming bookings
    breakdown: Dict               # raw numbers for frontend display