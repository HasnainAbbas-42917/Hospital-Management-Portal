from datetime import date, time
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app import models


def is_slot_within_availability(db: Session, doctor_id: int, appt_date: date, appt_time: time) -> bool:
    day_of_week = appt_date.weekday()  # 0=Monday
    availability = db.query(models.DoctorAvailability).filter(
        models.DoctorAvailability.doctor_id == doctor_id,
        models.DoctorAvailability.day_of_week == day_of_week,
        models.DoctorAvailability.start_time <= appt_time,
        models.DoctorAvailability.end_time > appt_time,
    ).first()
    return availability is not None


def is_slot_already_booked(db: Session, doctor_id: int, appt_date: date, appt_time: time) -> bool:
    existing = db.query(models.Appointment).filter(
        models.Appointment.doctor_id == doctor_id,
        models.Appointment.appointment_date == appt_date,
        models.Appointment.appointment_time == appt_time,
        models.Appointment.status.in_([
            models.AppointmentStatus.pending,
            models.AppointmentStatus.confirmed,
        ]),
    ).first()
    return existing is not None


def validate_and_create_appointment(db: Session, patient_id: int, doctor_id: int,
                                     appt_date: date, appt_time: time, reason: str | None):
    if not is_slot_within_availability(db, doctor_id, appt_date, appt_time):
        raise HTTPException(status_code=400, detail="Doctor is not available at this date/time")

    if is_slot_already_booked(db, doctor_id, appt_date, appt_time):
        raise HTTPException(status_code=409, detail="This slot is already booked")

    appointment = models.Appointment(
        patient_id=patient_id,
        doctor_id=doctor_id,
        appointment_date=appt_date,
        appointment_time=appt_time,
        reason=reason,
        status=models.AppointmentStatus.pending,
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment