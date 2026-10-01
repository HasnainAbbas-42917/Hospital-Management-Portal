from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.deps import require_role
from app import models, schemas

router = APIRouter(prefix="/doctors", tags=["Doctor Portal"])


def get_doctor_profile(current_user: models.User, db: Session) -> models.Doctor:
    doctor = db.query(models.Doctor).filter(models.Doctor.user_id == current_user.id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor profile not found")
    return doctor

@router.get("/me", response_model=schemas.DoctorOut)
def get_my_profile(
    current_user: models.User = Depends(require_role("doctor")),
    db: Session = Depends(get_db),
):
    return get_doctor_profile(current_user, db)


@router.patch("/me", response_model=schemas.DoctorOut)
def update_my_profile(
    profile_in: schemas.DoctorProfileUpdate,
    current_user: models.User = Depends(require_role("doctor")),
    db: Session = Depends(get_db),
):
    doctor = get_doctor_profile(current_user, db)

    if profile_in.name is not None:
        doctor.name = profile_in.name
    if profile_in.specialization is not None:
        doctor.specialization = profile_in.specialization
    if profile_in.experience_years is not None:
        doctor.experience_years = profile_in.experience_years
    if profile_in.bio is not None:
        doctor.bio = profile_in.bio
    if profile_in.requested_schedule_note is not None:
        doctor.requested_schedule_note = profile_in.requested_schedule_note

    db.commit()
    db.refresh(doctor)
    return doctor


# ---------- Availability ----------
@router.post("/availability", response_model=schemas.DoctorAvailabilityOut)
def add_availability(
    avail_in: schemas.DoctorAvailabilityCreate,
    current_user: models.User = Depends(require_role("doctor")),
    db: Session = Depends(get_db),
):
    doctor = get_doctor_profile(current_user, db)

    if avail_in.start_time >= avail_in.end_time:
        raise HTTPException(status_code=400, detail="Start time must be before end time")

    availability = models.DoctorAvailability(
        doctor_id=doctor.id,
        day_of_week=avail_in.day_of_week,
        start_time=avail_in.start_time,
        end_time=avail_in.end_time,
        slot_duration_minutes=avail_in.slot_duration_minutes,
    )
    db.add(availability)
    db.commit()
    db.refresh(availability)
    return availability


@router.get("/availability", response_model=List[schemas.DoctorAvailabilityOut])
def view_my_availability(
    current_user: models.User = Depends(require_role("doctor")),
    db: Session = Depends(get_db),
):
    doctor = get_doctor_profile(current_user, db)
    return db.query(models.DoctorAvailability).filter(
        models.DoctorAvailability.doctor_id == doctor.id
    ).all()


@router.delete("/availability/{availability_id}")
def delete_availability(
    availability_id: int,
    current_user: models.User = Depends(require_role("doctor")),
    db: Session = Depends(get_db),
):
    doctor = get_doctor_profile(current_user, db)
    slot = db.query(models.DoctorAvailability).filter(
        models.DoctorAvailability.id == availability_id,
        models.DoctorAvailability.doctor_id == doctor.id,
    ).first()
    if not slot:
        raise HTTPException(status_code=404, detail="Availability slot not found")

    db.delete(slot)
    db.commit()
    return {"detail": "Availability slot deleted"}


# ---------- Appointments ----------
@router.get("/appointments", response_model=List[schemas.AppointmentOut])
def my_appointments(
    current_user: models.User = Depends(require_role("doctor")),
    db: Session = Depends(get_db),
):
    doctor = get_doctor_profile(current_user, db)
    return db.query(models.Appointment).filter(
        models.Appointment.doctor_id == doctor.id
    ).all()


@router.patch("/appointments/{appointment_id}/status", response_model=schemas.AppointmentOut)
def update_appointment_status(
    appointment_id: int,
    status_in: schemas.AppointmentStatusUpdate,
    current_user: models.User = Depends(require_role("doctor")),
    db: Session = Depends(get_db),
):
    doctor = get_doctor_profile(current_user, db)
    appointment = db.query(models.Appointment).filter(
        models.Appointment.id == appointment_id,
        models.Appointment.doctor_id == doctor.id,
    ).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    appointment.status = status_in.status
    db.commit()
    db.refresh(appointment)
    return appointment


# ---------- Patients (only patients this doctor has appointments with) ----------
@router.get("/patients", response_model=List[schemas.PatientOut])
def my_patients(
    current_user: models.User = Depends(require_role("doctor")),
    db: Session = Depends(get_db),
):
    doctor = get_doctor_profile(current_user, db)
    patient_ids = db.query(models.Appointment.patient_id).filter(
        models.Appointment.doctor_id == doctor.id
    ).distinct()
    return db.query(models.Patient).filter(models.Patient.id.in_(patient_ids)).all()


# ---------- Medical Records ----------
@router.post("/appointments/{appointment_id}/medical-record", response_model=schemas.MedicalRecordOut)
def add_medical_record(
    appointment_id: int,
    record_in: schemas.MedicalRecordCreate,
    current_user: models.User = Depends(require_role("doctor")),
    db: Session = Depends(get_db),
):
    doctor = get_doctor_profile(current_user, db)
    appointment = db.query(models.Appointment).filter(
        models.Appointment.id == appointment_id,
        models.Appointment.doctor_id == doctor.id,
    ).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    existing = db.query(models.MedicalRecord).filter(
        models.MedicalRecord.appointment_id == appointment_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Medical record already exists for this appointment")

    record = models.MedicalRecord(
        patient_id=appointment.patient_id,
        doctor_id=doctor.id,
        appointment_id=appointment_id,
        diagnosis=record_in.diagnosis,
        prescription=record_in.prescription,
        notes=record_in.notes,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


# ---------- Reviews (view only — patients submit them) ----------
@router.get("/reviews", response_model=List[schemas.ReviewOut])
def my_reviews(
    current_user: models.User = Depends(require_role("doctor")),
    db: Session = Depends(get_db),
):
    doctor = get_doctor_profile(current_user, db)
    return db.query(models.Review).filter(models.Review.doctor_id == doctor.id).all()