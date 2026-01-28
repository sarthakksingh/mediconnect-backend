from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Doctor, Appointment
from app.schemas import AppointmentCreate, AppointmentReschedule
from app.agent import trigger_agent

router = APIRouter(prefix="", tags=["Patient"])


# ✅ Get all doctors
@router.get("/doctors")
def get_doctors(db: Session = Depends(get_db)):
    return db.query(Doctor).all()


# ✅ Get doctor availability
@router.get("/doctors/{doctor_id}/availability")
def get_availability(doctor_id: int, db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    return {"availability": doctor.availability}


# ✅ Book appointment
@router.post("/appointments/book")
def book_appointment(data: AppointmentCreate, db: Session = Depends(get_db)):
    appt = Appointment(**data.dict())
    db.add(appt)
    db.commit()
    db.refresh(appt)

    # Trigger AI agent reminder
    trigger_agent({
        "appointment_id": appt.id,
        "patient_id": data.patient_id,
        "doctor_id": data.doctor_id,
        "date_time": str(data.date_time),
        "type": "APPOINTMENT_CREATED"
    })

    return {"message": "Appointment Booked Successfully", "appointment_id": appt.id}


# ✅ Reschedule appointment
@router.put("/appointments/reschedule")
def reschedule_appointment(data: AppointmentReschedule, db: Session = Depends(get_db)):
    appt = db.query(Appointment).filter(Appointment.id == data.appointment_id).first()

    appt.date_time = data.new_date_time
    appt.status = "rescheduled"
    db.commit()

    # Trigger AI agent update reminder
    trigger_agent({
        "appointment_id": appt.id,
        "new_date_time": str(data.new_date_time),
        "type": "APPOINTMENT_RESCHEDULED"
    })

    return {"message": "Appointment Rescheduled Successfully"}
