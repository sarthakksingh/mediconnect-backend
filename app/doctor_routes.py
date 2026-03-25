from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Doctor, Report, Appointment, User
from app.schemas import AvailabilitySet, ReportReady, DoctorAppointmentOut
from app.auth import require_role, get_current_user
from app.agent import trigger_agent
from datetime import datetime, date

router = APIRouter(prefix="/doctor", tags=["Doctor"])


def get_doctor_record(current_user: User, db: Session) -> Doctor:
    """Helper: get the Doctor row linked to the logged-in user."""
    doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
    if not doctor:
        raise HTTPException(
            status_code=404,
            detail="No doctor profile found for this account. Contact admin."
        )
    return doctor


# ─── Dashboard summary ───────────────────────────────────

@router.get("/dashboard")
def doctor_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("DOCTOR"))
):
    doctor = get_doctor_record(current_user, db)
    today = date.today()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())

    today_appts = db.query(Appointment).filter(
        Appointment.doctor_id == doctor.id,
        Appointment.date_time >= today_start,
        Appointment.date_time <= today_end,
        Appointment.status != "cancelled"
    ).all()

    pending_count = db.query(Appointment).filter(
        Appointment.doctor_id == doctor.id,
        Appointment.status == "pending"
    ).count()

    total_patients = db.query(Appointment).filter(
        Appointment.doctor_id == doctor.id
    ).distinct(Appointment.patient_id).count()

    return {
        "doctor_id": doctor.id,
        "doctor_name": doctor.name,
        "specialization": doctor.specialization,
        "today_appointments": len(today_appts),
        "pending_requests": pending_count,
        "total_patients": total_patients,
    }


# ─── Today's appointments ────────────────────────────────

@router.get("/appointments/today")
def get_today_appointments(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("DOCTOR"))
):
    doctor = get_doctor_record(current_user, db)
    today = date.today()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())

    appts = db.query(Appointment).filter(
        Appointment.doctor_id == doctor.id,
        Appointment.date_time >= today_start,
        Appointment.date_time <= today_end,
        Appointment.status != "cancelled"
    ).order_by(Appointment.date_time).all()

    result = []
    for appt in appts:
        patient = db.query(User).filter(User.id == appt.patient_id).first()
        result.append({
            "appointment_id": appt.id,
            "patient_name": patient.name if patient else "Unknown",
            "patient_email": patient.email if patient else "",
            "patient_phone": patient.phone if patient else "",
            "date_time": appt.date_time,
            "reason": appt.reason,
            "status": appt.status
        })

    return result


# ─── All appointments (with optional status filter) ──────

@router.get("/appointments")
def get_all_appointments(
    status_filter: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("DOCTOR"))
):
    doctor = get_doctor_record(current_user, db)

    query = db.query(Appointment).filter(Appointment.doctor_id == doctor.id)
    if status_filter:
        query = query.filter(Appointment.status == status_filter)

    appts = query.order_by(Appointment.date_time.desc()).all()

    result = []
    for appt in appts:
        patient = db.query(User).filter(User.id == appt.patient_id).first()
        result.append({
            "appointment_id": appt.id,
            "patient_name": patient.name if patient else "Unknown",
            "patient_email": patient.email if patient else "",
            "patient_phone": patient.phone if patient else "",
            "date_time": appt.date_time,
            "reason": appt.reason,
            "status": appt.status
        })

    return result


# ─── Approve appointment ─────────────────────────────────

@router.put("/appointments/{appointment_id}/confirm")
def confirm_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("DOCTOR"))
):
    doctor = get_doctor_record(current_user, db)
    appt = db.query(Appointment).filter(
        Appointment.id == appointment_id,
        Appointment.doctor_id == doctor.id
    ).first()

    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")

    appt.status = "confirmed"
    db.commit()

    patient = db.query(User).filter(User.id == appt.patient_id).first()
    trigger_agent({
        "appointment_id": appt.id,
        "patient_name": patient.name if patient else "",
        "patient_email": patient.email if patient else "",
        "doctor_name": doctor.name,
        "date_time": str(appt.date_time),
        "type": "APPOINTMENT_CONFIRMED"
    })

    return {"message": "Appointment confirmed"}


# ─── Reject / cancel appointment ─────────────────────────

@router.put("/appointments/{appointment_id}/cancel")
def cancel_appointment_by_doctor(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("DOCTOR"))
):
    doctor = get_doctor_record(current_user, db)
    appt = db.query(Appointment).filter(
        Appointment.id == appointment_id,
        Appointment.doctor_id == doctor.id
    ).first()

    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")

    appt.status = "cancelled"
    db.commit()

    return {"message": "Appointment cancelled"}


# ─── Patient details ──────────────────────────────────────

@router.get("/patients/{patient_id}")
def get_patient_details(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("DOCTOR"))
):
    doctor = get_doctor_record(current_user, db)

    # Verify this patient has had an appointment with this doctor
    appt = db.query(Appointment).filter(
        Appointment.doctor_id == doctor.id,
        Appointment.patient_id == patient_id
    ).first()

    if not appt:
        raise HTTPException(status_code=403, detail="Patient not associated with this doctor")

    patient = db.query(User).filter(User.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    all_appts = db.query(Appointment).filter(
        Appointment.patient_id == patient_id,
        Appointment.doctor_id == doctor.id
    ).order_by(Appointment.date_time.desc()).all()

    return {
        "patient_id": patient.id,
        "name": patient.name,
        "email": patient.email,
        "phone": patient.phone,
        "appointments": [
            {
                "appointment_id": a.id,
                "date_time": a.date_time,
                "reason": a.reason,
                "status": a.status
            } for a in all_appts
        ]
    }


# ─── Set availability ────────────────────────────────────

@router.post("/availability")
def set_availability(
    data: AvailabilitySet,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("DOCTOR"))
):
    doctor = get_doctor_record(current_user, db)
    doctor.availability = data.availability
    db.commit()
    return {"message": "Availability updated"}


# ─── Set report ready date ───────────────────────────────

@router.post("/reports/set-ready-date")
def set_report_ready(
    data: ReportReady,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("DOCTOR"))
):
    doctor = get_doctor_record(current_user, db)
    appt = db.query(Appointment).filter(
        Appointment.id == data.appointment_id,
        Appointment.doctor_id == doctor.id
    ).first()

    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")

    patient = db.query(User).filter(User.id == appt.patient_id).first()

    report = Report(
        appointment_id=data.appointment_id,
        report_ready_date=data.report_ready_date
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    trigger_agent({
        "appointment_id": data.appointment_id,
        "report_ready_date": str(data.report_ready_date),
        "patient_name": patient.name if patient else "",
        "patient_email": patient.email if patient else "",
        "type": "REPORT_READY"
    })

    return {"message": "Report ready date saved", "report_id": report.id}