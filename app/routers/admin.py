from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.deps import require_role
from app import models, schemas, security
from app.services.notification_service import create_notification

router = APIRouter(prefix="/admin", tags=["Admin Portal"])


# ---------- Manage Doctors ----------
@router.get("/doctors")
def list_doctors(
    current_user: models.User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    doctors = db.query(models.Doctor).all()
    result = []
    for d in doctors:
        user = db.query(models.User).filter(models.User.id == d.user_id).first()
        slots = db.query(models.DoctorAvailability).filter(
            models.DoctorAvailability.doctor_id == d.id
        ).all()
        result.append({
            "id": d.id,
            "name": d.name,
            "specialization": d.specialization,
            "experience_years": d.experience_years,
            "bio": d.bio,
            "consultation_fee": float(d.consultation_fee) if d.consultation_fee is not None else 0,
            "status": d.status,
            "is_active": user.is_active if user else False,
            "working_days": sorted({s.day_of_week for s in slots}),
        })
    return result


@router.get("/doctors/applications")
def list_doctor_applications(
    status: str = "pending",
    current_user: models.User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    doctors = db.query(models.Doctor).filter(models.Doctor.status == status).all()
    return [
        {
            "id": d.id,
            "name": d.name,
            "specialization": d.specialization,
            "experience_years": d.experience_years,
            "bio": d.bio,
            "requested_schedule_note": d.requested_schedule_note,
        }
        for d in doctors
    ]


@router.patch("/doctors/{doctor_id}/approve")
def approve_doctor(
    doctor_id: int,
    current_user: models.User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    doctor = db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    doctor.status = "approved"
    db.commit()
    return {"detail": "Doctor approved and added to the hospital"}


@router.patch("/doctors/{doctor_id}/reject")
def reject_doctor(
    doctor_id: int,
    current_user: models.User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    doctor = db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    doctor.status = "rejected"
    db.commit()
    return {"detail": "Doctor application rejected"}


@router.patch("/doctors/{doctor_id}/fee")
def update_doctor_fee(
    doctor_id: int,
    fee_in: schemas.DoctorFeeUpdate,
    current_user: models.User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    doctor = db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    doctor.consultation_fee = fee_in.consultation_fee
    db.commit()
    return {"detail": "Fee updated successfully"}


@router.patch("/doctors/{doctor_id}/reactivate")
def reactivate_doctor(
    doctor_id: int,
    current_user: models.User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    doctor = db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    user = db.query(models.User).filter(models.User.id == doctor.user_id).first()
    if user:
        user.is_active = True
    db.commit()
    return {"detail": "Doctor account reactivated"}


@router.delete("/doctors/{doctor_id}")
def remove_doctor(
    doctor_id: int,
    current_user: models.User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    doctor = db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    user = db.query(models.User).filter(models.User.id == doctor.user_id).first()
    if user:
        user.is_active = False  # deactivate instead of hard delete, to preserve appointment history
    db.commit()
    return {"detail": "Doctor account deactivated"}


# ---------- Manage Receptionists ----------
@router.get("/receptionists")
def list_receptionists(
    current_user: models.User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    receptionists = db.query(models.Receptionist).all()
    result = []
    for r in receptionists:
        user = db.query(models.User).filter(models.User.id == r.user_id).first()
        result.append({"id": r.id, "name": r.name, "phone": r.phone, "is_active": user.is_active if user else False})
    return result


@router.post("/receptionists")
def create_receptionist(
    receptionist_in: schemas.ReceptionistCreate,
    current_user: models.User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    existing = db.query(models.User).filter(models.User.email == receptionist_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = models.User(
        email=receptionist_in.email,
        password_hash=security.hash_password(receptionist_in.password),
        role=models.RoleEnum.receptionist,
    )
    db.add(user)
    db.flush()

    receptionist = models.Receptionist(user_id=user.id, name=receptionist_in.name, phone=receptionist_in.phone)
    db.add(receptionist)
    db.commit()
    return {"detail": "Receptionist account created successfully"}


@router.patch("/receptionists/{receptionist_id}/reactivate")
def reactivate_receptionist(
    receptionist_id: int,
    current_user: models.User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    receptionist = db.query(models.Receptionist).filter(models.Receptionist.id == receptionist_id).first()
    if not receptionist:
        raise HTTPException(status_code=404, detail="Receptionist not found")
    user = db.query(models.User).filter(models.User.id == receptionist.user_id).first()
    if user:
        user.is_active = True
    db.commit()
    return {"detail": "Receptionist account reactivated"}


@router.delete("/receptionists/{receptionist_id}")
def remove_receptionist(
    receptionist_id: int,
    current_user: models.User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    receptionist = db.query(models.Receptionist).filter(models.Receptionist.id == receptionist_id).first()
    if not receptionist:
        raise HTTPException(status_code=404, detail="Receptionist not found")

    user = db.query(models.User).filter(models.User.id == receptionist.user_id).first()
    if user:
        user.is_active = False
    db.commit()
    return {"detail": "Receptionist account deactivated"}


# ---------- Manage Patients ----------
@router.get("/patients", response_model=List[schemas.PatientOut])
def list_patients(
    current_user: models.User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    return db.query(models.Patient).all()


# ---------- View All Appointments ----------
@router.get("/appointments")
def all_appointments(
    status: Optional[models.AppointmentStatus] = None,
    current_user: models.User = Depends(require_role("admin")),
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


# ---------- View Doctor Availability/Schedules ----------
@router.get("/doctors/{doctor_id}/availability", response_model=List[schemas.DoctorAvailabilityOut])
def view_doctor_schedule(
    doctor_id: int,
    current_user: models.User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    return db.query(models.DoctorAvailability).filter(
        models.DoctorAvailability.doctor_id == doctor_id
    ).all()


# ---------- Staff Attendance ----------
@router.get("/attendance")
def view_attendance(
    current_user: models.User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    records = db.query(models.StaffAttendance).order_by(models.StaffAttendance.date.desc()).all()
    result = []
    for r in records:
        user = db.query(models.User).filter(models.User.id == r.staff_user_id).first()
        name = "Unknown"
        role = None
        if user:
            role = getattr(user.role, "value", user.role)
            if user.doctor_profile:
                name = user.doctor_profile.name
            elif user.receptionist_profile:
                name = user.receptionist_profile.name
        result.append({
            "id": r.id,
            "staff_name": name,
            "role": role,
            "date": r.date,
            "check_in": r.check_in,
            "check_out": r.check_out,
            "status": r.status,
        })
    return result


# ---------- Reviews (view all) ----------
@router.get("/reviews")
def all_reviews(
    current_user: models.User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    reviews = db.query(models.Review).order_by(models.Review.created_at.desc()).all()
    result = []
    for r in reviews:
        patient = db.query(models.Patient).filter(models.Patient.id == r.patient_id).first()
        doctor = db.query(models.Doctor).filter(models.Doctor.id == r.doctor_id).first()
        result.append({
            "id": r.id,
            "rating": r.rating,
            "comment": r.comment,
            "created_at": r.created_at,
            "patient_id": r.patient_id,
            "patient_name": patient.name if patient else "Unknown",
            "doctor_id": r.doctor_id,
            "doctor_name": doctor.name if doctor else "Unknown",
            "doctor_specialization": doctor.specialization if doctor else None,
        })
    return result


# ---------- Basic Reports ----------
@router.get("/reports/summary")
def summary_report(
    current_user: models.User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    total_doctors = db.query(models.Doctor).count()
    total_patients = db.query(models.Patient).count()
    total_receptionists = db.query(models.Receptionist).count()
    total_appointments = db.query(models.Appointment).count()
    pending = db.query(models.Appointment).filter(
        models.Appointment.status == models.AppointmentStatus.pending
    ).count()
    confirmed = db.query(models.Appointment).filter(
        models.Appointment.status == models.AppointmentStatus.confirmed
    ).count()
    completed = db.query(models.Appointment).filter(
        models.Appointment.status == models.AppointmentStatus.completed
    ).count()
    cancelled = db.query(models.Appointment).filter(
        models.Appointment.status == models.AppointmentStatus.cancelled
    ).count()

    return {
        "total_doctors": total_doctors,
        "total_patients": total_patients,
        "total_receptionists": total_receptionists,
        "total_appointments": total_appointments,
        "appointments_pending": pending,
        "appointments_confirmed": confirmed,
        "appointments_completed": completed,
        "appointments_cancelled": cancelled,
    }
# ---------- Admin: Full Appointment Management ----------
@router.patch("/appointments/{appointment_id}/confirm", response_model=schemas.AppointmentOut)
def admin_confirm_appointment(
    appointment_id: int,
    current_user: models.User = Depends(require_role("admin")),
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
def admin_cancel_appointment(
    appointment_id: int,
    current_user: models.User = Depends(require_role("admin")),
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
def admin_reschedule_appointment(
    appointment_id: int,
    appt_in: schemas.AppointmentCreate,
    current_user: models.User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    appointment = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

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


@router.post("/appointments/{appointment_id}/payment", response_model=schemas.PaymentVerify)
def admin_verify_payment(
    appointment_id: int,
    payment_in: schemas.PaymentVerify,
    current_user: models.User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    appointment = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    existing = db.query(models.Payment).filter(models.Payment.appointment_id == appointment_id).first()
    if existing:
        existing.amount = payment_in.amount
        existing.method = payment_in.method
        existing.status = payment_in.status
        db.commit()
        db.refresh(existing)
        return payment_in

    payment = models.Payment(
        appointment_id=appointment_id,
        amount=payment_in.amount,
        method=payment_in.method,
        status=payment_in.status,
    )
    db.add(payment)
    db.commit()
    return payment_in
