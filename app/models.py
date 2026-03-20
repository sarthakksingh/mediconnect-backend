from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, JSON
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


# 👨‍⚕️ Doctor Table
class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    specialization = Column(String)
    experience_years = Column(Integer, default=0)
    patients_count = Column(Integer, default=0)
    availability = Column(JSON)  # stored as JSON slots


# 📅 Appointment Table
class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    date_time = Column(DateTime, nullable=False)
    reason = Column(String, nullable=True)
    status = Column(String, default="booked")  # booked / rescheduled / completed / cancelled


# 📄 Report Table
class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=False)
    report_ready_date = Column(DateTime)
    notified = Column(Boolean, default=False)