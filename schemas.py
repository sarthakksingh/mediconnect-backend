from pydantic import BaseModel
from datetime import datetime
from typing import Dict


# Appointment Booking Request
class AppointmentCreate(BaseModel):
    patient_id: int
    doctor_id: int
    date_time: datetime


# Appointment Reschedule Request
class AppointmentReschedule(BaseModel):
    appointment_id: int
    new_date_time: datetime


# Doctor Availability Set Request
class AvailabilitySet(BaseModel):
    doctor_id: int
    availability: Dict


# Report Ready Date Request
class ReportReady(BaseModel):
    appointment_id: int
    report_ready_date: datetime
