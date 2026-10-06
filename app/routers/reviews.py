from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.deps import require_role
from app import models, schemas

router = APIRouter(prefix="/reviews", tags=["Reviews"])


def get_patient_profile(current_user: models.User, db: Session) -> models.Patient:
    patient = db.query(models.Patient).filter(models.Patient.user_id == current_user.id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    return patient


@router.post("", response_model=schemas.ReviewOut)
def submit_review(
    review_in: schemas.ReviewCreate,
    current_user: models.User = Depends(require_role("patient")),
    db: Session = Depends(get_db),
):
    patient = get_patient_profile(current_user, db)

    appointment = db.query(models.Appointment).filter(
        models.Appointment.id == review_in.appointment_id,
        models.Appointment.patient_id == patient.id,
    ).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    if appointment.status != models.AppointmentStatus.completed:
        raise HTTPException(status_code=400, detail="You can only review a completed appointment")

    existing = db.query(models.Review).filter(
        models.Review.appointment_id == review_in.appointment_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="You have already reviewed this appointment")

    if not (1 <= review_in.rating <= 5):
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")

    review = models.Review(
        patient_id=patient.id,
        doctor_id=appointment.doctor_id,
        appointment_id=review_in.appointment_id,
        rating=review_in.rating,
        comment=review_in.comment,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


@router.get("/public")
def get_public_reviews(db: Session = Depends(get_db)):
    reviews = (
        db.query(
            models.Review.id,
            models.Review.rating,
            models.Review.comment,
            models.Review.created_at,
            models.Patient.name.label("patient_name"),
            models.Doctor.name.label("doctor_name"),
            models.Doctor.specialization.label("doctor_specialization"),
        )
        .outerjoin(models.Patient, models.Patient.id == models.Review.patient_id)
        .outerjoin(models.Doctor, models.Doctor.id == models.Review.doctor_id)
        .order_by(models.Review.created_at.desc(), models.Review.id.desc())
        .all()
    )
    return [
        {
            "id": review.id,
            "rating": review.rating,
            "comment": review.comment,
            "created_at": review.created_at,
            "patient_name": review.patient_name or "Unknown patient",
            "doctor_name": review.doctor_name or "Unknown doctor",
            "doctor_specialization": review.doctor_specialization or "General",
        }
        for review in reviews
    ]


@router.get("/doctor/{doctor_id}", response_model=List[schemas.ReviewOut])
def get_doctor_reviews(doctor_id: int, db: Session = Depends(get_db)):
    # Public: anyone (even not logged in) can view a doctor's reviews before booking
    return db.query(models.Review).filter(models.Review.doctor_id == doctor_id).all()