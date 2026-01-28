from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, JSON
from app.database import Base


# 👤 User Table
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    phone = Column(String)
    email = Column(String, unique=True)
    role = Column(String)  # PATIENT / DOCTOR / ADMIN


# 👨‍⚕️ Doctor Table
class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    specialization = Column(String)
    availability = Column(JSON)  # stored as JSON slots


# 📅 Appointment Table
class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"))
    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    date_time = Column(DateTime)
    status = Column(String, default="booked")


# 📄 Report Table
class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id"))
    report_ready_date = Column(DateTime)
    notified = Column(Boolean, default=False)
