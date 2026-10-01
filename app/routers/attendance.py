from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.deps import require_role
from app import models, schemas

router = APIRouter(prefix="/attendance", tags=["Staff Attendance"])

PKT = timezone(timedelta(hours=5))  # Pakistan Standard Time (UTC+5, no daylight saving)


def today_pkt():
    return datetime.now(PKT).date()


def utc_now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


@router.post("/check-in", response_model=schemas.AttendanceOut)
def check_in(
    current_user: models.User = Depends(require_role("doctor", "receptionist")),
    db: Session = Depends(get_db),
):
    today = today_pkt()
    existing = db.query(models.StaffAttendance).filter(
        models.StaffAttendance.staff_user_id == current_user.id,
        models.StaffAttendance.date == today,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already checked in today")

    record = models.StaffAttendance(
        staff_user_id=current_user.id,
        date=today,
        check_in=utc_now(),
        status="present",
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.post("/check-out", response_model=schemas.AttendanceOut)
def check_out(
    current_user: models.User = Depends(require_role("doctor", "receptionist")),
    db: Session = Depends(get_db),
):
    today = today_pkt()
    record = db.query(models.StaffAttendance).filter(
        models.StaffAttendance.staff_user_id == current_user.id,
        models.StaffAttendance.date == today,
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="You have not checked in today")
    if record.check_out:
        raise HTTPException(status_code=400, detail="Already checked out today")

    record.check_out = utc_now()
    db.commit()
    db.refresh(record)
    return record


@router.get("/my-history", response_model=list[schemas.AttendanceOut])
def my_attendance_history(
    current_user: models.User = Depends(require_role("doctor", "receptionist")),
    db: Session = Depends(get_db),
):
    return db.query(models.StaffAttendance).filter(
        models.StaffAttendance.staff_user_id == current_user.id
    ).order_by(models.StaffAttendance.date.desc()).all()