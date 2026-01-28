from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Doctor, Report
from app.schemas import AvailabilitySet, ReportReady
from app.agent import trigger_agent


router = APIRouter(prefix="", tags=["Doctor"])


# ✅ Doctor sets availability
@router.post("/availability/set")
def set_availability(data: AvailabilitySet, db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(Doctor.id == data.doctor_id).first()

    doctor.availability = data.availability
    db.commit()

    return {"message": "Doctor Availability Updated"}


# ✅ Doctor sets report ready date
@router.post("/reports/set-ready-date")
def set_report_ready(data: ReportReady, db: Session = Depends(get_db)):
    report = Report(
        appointment_id=data.appointment_id,
        report_ready_date=data.report_ready_date
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    # Trigger AI agent notification
    trigger_agent({
        "appointment_id": data.appointment_id,
        "report_ready_date": str(data.report_ready_date),
        "type": "REPORT_READY"
    })

    return {"message": "Report Ready Date Saved Successfully"}
