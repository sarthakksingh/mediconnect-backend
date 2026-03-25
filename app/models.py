from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, JSON, Date
from app.database import Base


# 👤 User Table
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="PATIENT")  # PATIENT / DOCTOR / ADMIN

    # Profile fields (V2)
    blood_group = Column(String, nullable=True)   # e.g. "A+", "O-"
    date_of_birth = Column(Date, nullable=True)
    gender = Column(String, nullable=True)        # "Male" / "Female" / "Other"


# 👨‍⚕️ Doctor Table
class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, unique=True)
    name = Column(String, nullable=False)
    specialization = Column(String)
    experience_years = Column(Integer, default=0)
    patients_count = Column(Integer, default=0)
    availability = Column(JSON)


# 📅 Appointment Table
class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    date_time = Column(DateTime, nullable=False)
    reason = Column(String, nullable=True)
    status = Column(String, default="pending")  # pending / confirmed / completed / cancelled / rescheduled


# 📄 Report Table
class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=False)
    report_ready_date = Column(DateTime)
    notified = Column(Boolean, default=False)


# 💊 Medicine Table (patient self-managed)
class Medicine(Base):
    __tablename__ = "medicines"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)           # e.g. "Metformin"
    dosage = Column(String, nullable=True)          # e.g. "500mg"
    frequency = Column(String, nullable=True)       # e.g. "Twice daily"
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)          # null = ongoing
    is_active = Column(Boolean, default=True)
    notes = Column(String, nullable=True)