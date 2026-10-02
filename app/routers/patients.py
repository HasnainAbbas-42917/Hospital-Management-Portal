from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from app.database import get_db
from app.deps import require_role
from app import models, schemas
from app.services.appointment_logic import validate_and_create_appointment

router = APIRouter(prefix="/patients", tags=["Patient Portal"])


def get_patient_profile(current_user: models.User, db: Session) -> models.Patient:
    patient = db.query(models.Patient).filter(models.Patient.user_id == current_user.id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    return patient

@router.get("/me", response_model=schemas.PatientOut)
def get_my_profile(
    current_user: models.User = Depends(require_role("patient")),
    db: Session = Depends(get_db),
):
    return get_patient_profile(current_user, db)


@router.patch("/me", response_model=schemas.PatientOut)
def update_my_profile(
    profile_in: schemas.PatientProfileUpdate,
    current_user: models.User = Depends(require_role("patient")),
    db: Session = Depends(get_db),
):
    patient = get_patient_profile(current_user, db)

    if profile_in.name is not None:
        patient.name = profile_in.name
    if profile_in.phone is not None:
        patient.phone = profile_in.phone
    if profile_in.dob is not None:
        patient.dob = profile_in.dob
    if profile_in.gender is not None:
        patient.gender = profile_in.gender
    if profile_in.address is not None:
        patient.address = profile_in.address

    db.commit()
    db.refresh(patient)
    return patient


@router.get("/doctors/search", response_model=List[schemas.DoctorOut])
def search_doctors(
    specialization: Optional[str] = None,
    keyword: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(models.Doctor).filter(models.Doctor.status == "approved")
    if specialization:
        query = query.filter(models.Doctor.specialization.ilike(f"%{specialization}%"))
    if keyword:
        query = query.filter(
            (models.Doctor.name.ilike(f"%{keyword}%")) |
            (models.Doctor.bio.ilike(f"%{keyword}%"))
        )
    return query.all()


@router.post("/appointments", response_model=schemas.AppointmentOut)
def request_appointment(
    appt_in: schemas.AppointmentCreate,
    current_user: models.User = Depends(require_role("patient")),
    db: Session = Depends(get_db),
):
    patient = get_patient_profile(current_user, db)
    appointment = validate_and_create_appointment(
        db, patient.id, appt_in.doctor_id, appt_in.appointment_date,
        appt_in.appointment_time, appt_in.reason,
    )
    return appointment


@router.get("/appointments", response_model=List[schemas.AppointmentOut])
def my_appointments(
    current_user: models.User = Depends(require_role("patient")),
    db: Session = Depends(get_db),
):
    patient = get_patient_profile(current_user, db)
    return db.query(models.Appointment).filter(models.Appointment.patient_id == patient.id).all()

@router.get("/medical-records")
def my_medical_records(
    current_user: models.User = Depends(require_role("patient")),
    db: Session = Depends(get_db),
):
    patient = get_patient_profile(current_user, db)
    records = db.query(models.MedicalRecord).filter(
        models.MedicalRecord.patient_id == patient.id
    ).order_by(models.MedicalRecord.created_at.desc()).all()

    result = []
    for r in records:
        appointment = db.query(models.Appointment).filter(models.Appointment.id == r.appointment_id).first()
        doctor = db.query(models.Doctor).filter(models.Doctor.id == r.doctor_id).first()
        result.append({
            "id": r.id,
            "diagnosis": r.diagnosis,
            "prescription": r.prescription,
            "notes": r.notes,
            "created_at": r.created_at,
            "doctor_name": doctor.name if doctor else "Unknown",
            "doctor_specialization": doctor.specialization if doctor else None,
            "appointment_date": appointment.appointment_date if appointment else None,
        })
    return result