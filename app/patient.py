from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Doctor, Appointment, User, Medicine
from app.schemas import (
    AppointmentCreate, AppointmentReschedule,
    UserProfileOut, UserProfileUpdate,
    MedicineCreate, MedicineOut, MedicineUpdate,
    HealthScoreOut
)
from app.agent import trigger_agent
from app.auth import get_current_user
from datetime import datetime, timedelta, date
from typing import List 

router = APIRouter(prefix="", tags=["Patient"])


# ─── Doctors ─────────────────────────────────────────────

@router.get("/doctors")
def get_doctors(db: Session = Depends(get_db)):
    return db.query(Doctor).all()


@router.get("/doctors/{doctor_id}/availability")
def get_availability(doctor_id: int, db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail=f"Doctor with id {doctor_id} not found")
    return {"doctor_id": doctor_id, "availability": doctor.availability}


# ─── Profile ─────────────────────────────────────────────

@router.get("/users/me", response_model=UserProfileOut)
def get_my_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Return full profile of the logged-in user."""
    return current_user


@router.patch("/users/me", response_model=UserProfileOut)
def update_my_profile(
    data: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update editable profile fields. Only provided fields are updated."""
    update_data = data.dict(exclude_unset=True)

    for field, value in update_data.items():
        setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)

    # Keep localStorage in sync — frontend uses the name
    return current_user


# ─── Appointments ─────────────────────────────────────────

@router.post("/appointments/book", status_code=201)
def book_appointment(
    data: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.id != data.patient_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only book appointments for yourself"
        )

    patient = db.query(User).filter(User.id == data.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

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


@router.put("/appointments/reschedule")
def reschedule_appointment(
    data: AppointmentReschedule,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    appt = db.query(Appointment).filter(Appointment.id == data.appointment_id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")

    if appt.patient_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only reschedule your own appointments"
        )

    appt.date_time = data.new_date_time
    appt.status = "rescheduled"
    db.commit()

    trigger_agent({
        "appointment_id": appt.id,
        "new_date_time": str(data.new_date_time),
        "type": "APPOINTMENT_RESCHEDULED"
    })

    return {"message": "Appointment Rescheduled Successfully"}


@router.get("/appointments/my/{patient_id}")
def get_my_appointments(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.id != patient_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own appointments"
        )

    appointments = db.query(Appointment).filter(
        Appointment.patient_id == patient_id
    ).order_by(Appointment.date_time.desc()).all()

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


@router.put("/appointments/cancel/{appointment_id}")
def cancel_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    appt = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")

    if appt.patient_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only cancel your own appointments"
        )

    appt.status = "cancelled"
    db.commit()

    return {"message": "Appointment Cancelled Successfully"}


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


# ─── Medicines ────────────────────────────────────────────

@router.post("/medicines", response_model=MedicineOut, status_code=201)
def add_medicine(
    data: MedicineCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    med = Medicine(
        patient_id=current_user.id,
        name=data.name,
        dosage=data.dosage,
        frequency=data.frequency,
        start_date=data.start_date or date.today(),
        end_date=data.end_date,
        is_active=True,
        notes=data.notes
    )
    db.add(med)
    db.commit()
    db.refresh(med)
    return med


@router.get("/medicines/my", response_model=List[MedicineOut])
def get_my_medicines(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Medicine).filter(
        Medicine.patient_id == current_user.id
    ).order_by(Medicine.is_active.desc(), Medicine.start_date.desc()).all()


@router.patch("/medicines/{medicine_id}", response_model=MedicineOut)
def update_medicine(
    medicine_id: int,
    data: MedicineUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    med = db.query(Medicine).filter(
        Medicine.id == medicine_id,
        Medicine.patient_id == current_user.id
    ).first()
    if not med:
        raise HTTPException(status_code=404, detail="Medicine not found")

    for field, value in data.dict(exclude_unset=True).items():
        setattr(med, field, value)

    db.commit()
    db.refresh(med)
    return med


@router.delete("/medicines/{medicine_id}", status_code=204)
def delete_medicine(
    medicine_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    med = db.query(Medicine).filter(
        Medicine.id == medicine_id,
        Medicine.patient_id == current_user.id
    ).first()
    if not med:
        raise HTTPException(status_code=404, detail="Medicine not found")

    db.delete(med)
    db.commit()


# ─── Health Score ─────────────────────────────────────────

@router.get("/health-score", response_model=HealthScoreOut)
def get_health_score(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Score breakdown (all out of 100):
      - Completion rate  → 50 pts  (completed / total non-cancelled appts)
      - Adherence score  → 30 pts  (active medicines / total medicines, or 100% if none)
      - Streak score     → 20 pts  (has upcoming confirmed/pending appt = 20, else 0)
    """
    appointments = db.query(Appointment).filter(
        Appointment.patient_id == current_user.id
    ).all()

    non_cancelled = [a for a in appointments if a.status != "cancelled"]
    completed = [a for a in non_cancelled if a.status == "completed"]

    completion_rate = (len(completed) / len(non_cancelled) * 100) if non_cancelled else 0.0

    # Adherence: ratio of active medicines to total; 100% if patient has no medicines yet
    medicines = db.query(Medicine).filter(
        Medicine.patient_id == current_user.id
    ).all()
    active_meds = [m for m in medicines if m.is_active]
    adherence_rate = (len(active_meds) / len(medicines) * 100) if medicines else 100.0

    # Streak: does the patient have an upcoming appointment?
    now = datetime.utcnow()
    upcoming = [
        a for a in appointments
        if a.date_time > now and a.status in ("pending", "confirmed", "rescheduled")
    ]
    streak_score = 100.0 if upcoming else 0.0

    # Weighted total
    total = (
        completion_rate * 0.50 +
        adherence_rate  * 0.30 +
        streak_score    * 0.20
    )

    return HealthScoreOut(
        score=round(total),
        completion_rate=round(completion_rate, 1),
        adherence_score=round(adherence_rate, 1),
        streak_score=round(streak_score, 1),
        breakdown={
            "total_appointments": len(non_cancelled),
            "completed_appointments": len(completed),
            "total_medicines": len(medicines),
            "active_medicines": len(active_meds),
            "has_upcoming": len(upcoming) > 0,
            "upcoming_count": len(upcoming)
        }
    )