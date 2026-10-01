from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.deps import require_role
from app import models, schemas
from app.services.notification_service import create_notification

router = APIRouter(prefix="/receptionist", tags=["Receptionist Portal"])


def get_receptionist_profile(current_user: models.User, db: Session) -> models.Receptionist:
    receptionist = db.query(models.Receptionist).filter(
        models.Receptionist.user_id == current_user.id
    ).first()
    if not receptionist:
        raise HTTPException(status_code=404, detail="Receptionist profile not found")
    return receptionist

@router.get("/me")
def get_my_profile(
    current_user: models.User = Depends(require_role("receptionist")),
    db: Session = Depends(get_db),
):
    r = get_receptionist_profile(current_user, db)
    return {"id": r.id, "name": r.name, "phone": r.phone}


@router.patch("/me")
def update_my_profile(
    profile_in: schemas.ReceptionistProfileUpdate,
    current_user: models.User = Depends(require_role("receptionist")),
    db: Session = Depends(get_db),
):
    r = get_receptionist_profile(current_user, db)
    if profile_in.name is not None:
        r.name = profile_in.name
    if profile_in.phone is not None:
        r.phone = profile_in.phone
    db.commit()
    db.refresh(r)
    return {"id": r.id, "name": r.name, "phone": r.phone}


# ---------- View Appointments ----------
@router.get("/appointments")
def view_appointments(
    status: Optional[models.AppointmentStatus] = None,
    current_user: models.User = Depends(require_role("receptionist")),
    db: Session = Depends(get_db),
):
    query = db.query(models.Appointment)
    if status:
        query = query.filter(models.Appointment.status == status)
    appointments = query.all()

    result = []
    for a in appointments:
        result.append({
            "id": a.id,
            "appointment_date": a.appointment_date,
            "appointment_time": a.appointment_time,
            "status": a.status,
            "reason": a.reason,
            "patient_id": a.patient_id,
            "patient_name": a.patient.name if a.patient else "Unknown",
            "patient_phone": a.patient.phone if a.patient else None,
            "doctor_id": a.doctor_id,
            "doctor_name": a.doctor.name if a.doctor else "Unknown",
            "doctor_specialization": a.doctor.specialization if a.doctor else None,
        })
    return result

# ---------- Confirm / Cancel / Reschedule ----------
@router.patch("/appointments/{appointment_id}/confirm", response_model=schemas.AppointmentOut)
def confirm_appointment(
    appointment_id: int,
    current_user: models.User = Depends(require_role("receptionist")),
    db: Session = Depends(get_db),
):
    appointment = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    appointment.status = models.AppointmentStatus.confirmed
    db.commit()
    db.refresh(appointment)

    patient_user_id = appointment.patient.user_id
    create_notification(db, patient_user_id, f"Your appointment on {appointment.appointment_date} at {appointment.appointment_time} has been confirmed.")

    return appointment


@router.patch("/appointments/{appointment_id}/cancel", response_model=schemas.AppointmentOut)
def cancel_appointment(
    appointment_id: int,
    current_user: models.User = Depends(require_role("receptionist")),
    db: Session = Depends(get_db),
):
    appointment = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    appointment.status = models.AppointmentStatus.cancelled
    db.commit()
    db.refresh(appointment)

    patient_user_id = appointment.patient.user_id
    create_notification(db, patient_user_id, f"Your appointment on {appointment.appointment_date} at {appointment.appointment_time} has been cancelled.")

    return appointment


@router.patch("/appointments/{appointment_id}/reschedule", response_model=schemas.AppointmentOut)
def reschedule_appointment(
    appointment_id: int,
    appt_in: schemas.AppointmentCreate,
    current_user: models.User = Depends(require_role("receptionist")),
    db: Session = Depends(get_db),
):
    appointment = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    # Check the new slot isn't already taken by someone else
    conflict = db.query(models.Appointment).filter(
        models.Appointment.doctor_id == appointment.doctor_id,
        models.Appointment.appointment_date == appt_in.appointment_date,
        models.Appointment.appointment_time == appt_in.appointment_time,
        models.Appointment.id != appointment_id,
        models.Appointment.status.in_([models.AppointmentStatus.pending, models.AppointmentStatus.confirmed]),
    ).first()
    if conflict:
        raise HTTPException(status_code=409, detail="New slot is already booked")

    appointment.appointment_date = appt_in.appointment_date
    appointment.appointment_time = appt_in.appointment_time
    db.commit()
    db.refresh(appointment)
    return appointment


# ---------- Doctor Availability (view only) ----------
@router.get("/doctors/{doctor_id}/availability", response_model=List[schemas.DoctorAvailabilityOut])
def check_doctor_availability(
    doctor_id: int,
    current_user: models.User = Depends(require_role("receptionist")),
    db: Session = Depends(get_db),
):
    return db.query(models.DoctorAvailability).filter(
        models.DoctorAvailability.doctor_id == doctor_id
    ).all()


# ---------- Patient Details ----------
@router.get("/patients/{patient_id}", response_model=schemas.PatientOut)
def view_patient(
    patient_id: int,
    current_user: models.User = Depends(require_role("receptionist")),
    db: Session = Depends(get_db),
):
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


# ---------- Payment Verification ----------
@router.post("/appointments/{appointment_id}/payment", response_model=schemas.PaymentVerify)
def verify_payment(
    appointment_id: int,
    payment_in: schemas.PaymentVerify,
    current_user: models.User = Depends(require_role("receptionist")),
    db: Session = Depends(get_db),
):
    receptionist = get_receptionist_profile(current_user, db)
    appointment = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    existing = db.query(models.Payment).filter(models.Payment.appointment_id == appointment_id).first()
    if existing:
        existing.amount = payment_in.amount
        existing.method = payment_in.method
        existing.status = payment_in.status
        existing.verified_by = receptionist.id
        db.commit()
        db.refresh(existing)
        return payment_in

    payment = models.Payment(
        appointment_id=appointment_id,
        amount=payment_in.amount,
        method=payment_in.method,
        status=payment_in.status,
        verified_by=receptionist.id,
    )
    db.add(payment)
    db.commit()
    return payment_in