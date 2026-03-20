from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import Doctor, Appointment, User
from app.schemas import AppointmentCreate, AppointmentReschedule
from app.agent import trigger_agent
from datetime import datetime, timedelta

router = APIRouter(prefix="", tags=["Patient"])


# ✅ Get all doctors
@router.get("/doctors")
def get_doctors(db: Session = Depends(get_db)):
    doctors = db.query(Doctor).all()
    return doctors


# ✅ Get doctor availability
@router.get("/doctors/{doctor_id}/availability")
def get_availability(doctor_id: int, db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Doctor with id {doctor_id} not found"
        )
    return {"doctor_id": doctor_id, "availability": doctor.availability}


# ✅ Book appointment
@router.post("/appointments/book", status_code=201)
def book_appointment(data: AppointmentCreate, db: Session = Depends(get_db)):
    # Verify patient exists
    patient = db.query(User).filter(User.id == data.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Verify doctor exists
    doctor = db.query(Doctor).filter(Doctor.id == data.doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    appt = Appointment(
        patient_id=data.patient_id,
        doctor_id=data.doctor_id,
        date_time=data.date_time,
        reason=data.reason
    )
    db.add(appt)
    db.commit()
    db.refresh(appt)

    # Trigger n8n appointment reminder workflow
    trigger_agent({
        "appointment_id": appt.id,
        "patient_id": data.patient_id,
        "patient_name": patient.name,
        "patient_email": patient.email,
        "doctor_name": doctor.name,
        "date_time": str(data.date_time),
        "type": "APPOINTMENT_CREATED"
    })

    return {"message": "Appointment Booked Successfully", "appointment_id": appt.id}


# ✅ Reschedule appointment
@router.put("/appointments/reschedule")
def reschedule_appointment(data: AppointmentReschedule, db: Session = Depends(get_db)):
    appt = db.query(Appointment).filter(Appointment.id == data.appointment_id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")

    appt.date_time = data.new_date_time
    appt.status = "rescheduled"
    db.commit()

    # Trigger n8n rescheduled reminder
    trigger_agent({
        "appointment_id": appt.id,
        "new_date_time": str(data.new_date_time),
        "type": "APPOINTMENT_RESCHEDULED"
    })

    return {"message": "Appointment Rescheduled Successfully"}


# ✅ Get appointments for a specific patient (for dashboard + bookings page)
@router.get("/appointments/my/{patient_id}")
def get_my_appointments(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(User).filter(User.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    appointments = db.query(Appointment).filter(
        Appointment.patient_id == patient_id
    ).all()

    # Enrich with doctor name
    result = []
    for appt in appointments:
        doctor = db.query(Doctor).filter(Doctor.id == appt.doctor_id).first()
        result.append({
            "appointment_id": appt.id,
            "doctor_name": doctor.name if doctor else "Unknown",
            "doctor_specialization": doctor.specialization if doctor else "",
            "date_time": appt.date_time,
            "reason": appt.reason,
            "status": appt.status
        })

    return result


# ✅ Get tomorrow's appointments (used by n8n Appointment Reminder workflow)
@router.get("/appointments/tomorrow")
def get_tomorrow_appointments(db: Session = Depends(get_db)):
    tomorrow = datetime.utcnow().date() + timedelta(days=1)
    tomorrow_start = datetime.combine(tomorrow, datetime.min.time())
    tomorrow_end = datetime.combine(tomorrow, datetime.max.time())

    appointments = db.query(Appointment).filter(
        Appointment.date_time >= tomorrow_start,
        Appointment.date_time <= tomorrow_end,
        Appointment.status == "booked"
    ).all()

    result = []
    for appt in appointments:
        patient = db.query(User).filter(User.id == appt.patient_id).first()
        doctor = db.query(Doctor).filter(Doctor.id == appt.doctor_id).first()
        result.append({
            "appointment_id": appt.id,
            "patient_name": patient.name if patient else "Unknown",
            "patient_email": patient.email if patient else "",
            "doctor_name": doctor.name if doctor else "Unknown",
            "appointment_datetime": str(appt.date_time)
        })

    return result


# ✅ Cancel appointment
@router.put("/appointments/cancel/{appointment_id}")
def cancel_appointment(appointment_id: int, db: Session = Depends(get_db)):
    appt = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")

    appt.status = "cancelled"
    db.commit()

    return {"message": "Appointment Cancelled Successfully"}