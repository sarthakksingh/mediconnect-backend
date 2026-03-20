from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Doctor, Report, Appointment, User
from app.schemas import AvailabilitySet, ReportReady
from app.agent import trigger_agent

router = APIRouter(prefix="", tags=["Doctor"])


# ✅ Doctor sets availability
@router.post("/availability/set")
def set_availability(data: AvailabilitySet, db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(Doctor.id == data.doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    doctor.availability = data.availability
    db.commit()

    return {"message": "Doctor Availability Updated"}


# ✅ Doctor sets report ready date → triggers n8n notification
@router.post("/reports/set-ready-date")
def set_report_ready(data: ReportReady, db: Session = Depends(get_db)):
    # Verify appointment exists
    appt = db.query(Appointment).filter(Appointment.id == data.appointment_id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")

    # Get patient details for notification
    patient = db.query(User).filter(User.id == appt.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    report = Report(
        appointment_id=data.appointment_id,
        report_ready_date=data.report_ready_date
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    # Trigger n8n report notification with full patient info
    trigger_agent({
        "appointment_id": data.appointment_id,
        "report_ready_date": str(data.report_ready_date),
        "patient_name": patient.name,
        "patient_email": patient.email,
        "type": "REPORT_READY"
    })

    return {"message": "Report Ready Date Saved Successfully", "report_id": report.id}


# ✅ Get all doctors
@router.get("/doctors/all")
def get_all_doctors(db: Session = Depends(get_db)):
    return db.query(Doctor).all()