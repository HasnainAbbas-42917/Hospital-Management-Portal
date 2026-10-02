"""
Seed script: populates the database with realistic demo data.
Run from the project root (venv activated):
    python seed_data.py
Safe to re-run — it skips records that already exist, cleans up old
@example.com test patients, and corrects gender on existing patients.
"""

import random
from datetime import date, time, datetime, timedelta

from app.database import SessionLocal, engine, Base
from app import models, security

Base.metadata.create_all(bind=engine)
db = SessionLocal()

PASSWORD = "Password123"  # same password for every seeded account, for easy testing

# ---------------------------------------------------------------------------
# TASK 1 — Remove old @example.com test patients and everything linked to them
# ---------------------------------------------------------------------------

print("=" * 70)
print("STEP 0: Cleaning up old @example.com patient accounts")
print("=" * 70)

old_patient_users = db.query(models.User).filter(
    models.User.email.like("patient%@example.com")
).all()

if not old_patient_users:
    print("No old @example.com patients found. Nothing to clean up.\n")
else:
    old_user_ids = [u.id for u in old_patient_users]
    old_patients = db.query(models.Patient).filter(models.Patient.user_id.in_(old_user_ids)).all()
    old_patient_ids = [p.id for p in old_patients]

    old_appointments = db.query(models.Appointment).filter(
        models.Appointment.patient_id.in_(old_patient_ids)
    ).all()
    old_appointment_ids = [a.id for a in old_appointments]

    review_count = db.query(models.Review).filter(models.Review.patient_id.in_(old_patient_ids)).count()
    record_count = db.query(models.MedicalRecord).filter(models.MedicalRecord.patient_id.in_(old_patient_ids)).count()
    payment_count = db.query(models.Payment).filter(models.Payment.appointment_id.in_(old_appointment_ids)).count()
    notification_count = db.query(models.Notification).filter(models.Notification.user_id.in_(old_user_ids)).count()

    print("The following will be PERMANENTLY deleted:")
    print(f"  - {len(old_patient_ids)} patient profiles (emails patient1..50@example.com)")
    print(f"  - {len(old_user_ids)} user login accounts")
    print(f"  - {len(old_appointment_ids)} appointments")
    print(f"  - {payment_count} payments")
    print(f"  - {record_count} medical records")
    print(f"  - {review_count} reviews")
    print(f"  - {notification_count} notifications")
    print("Gmail patients, doctors, receptionists, and admins are NOT affected.\n")

    try:
        db.query(models.Review).filter(models.Review.patient_id.in_(old_patient_ids)).delete(synchronize_session=False)
        db.query(models.MedicalRecord).filter(models.MedicalRecord.patient_id.in_(old_patient_ids)).delete(synchronize_session=False)
        db.query(models.Payment).filter(models.Payment.appointment_id.in_(old_appointment_ids)).delete(synchronize_session=False)
        db.query(models.Appointment).filter(models.Appointment.patient_id.in_(old_patient_ids)).delete(synchronize_session=False)
        db.query(models.Notification).filter(models.Notification.user_id.in_(old_user_ids)).delete(synchronize_session=False)
        db.query(models.Patient).filter(models.Patient.id.in_(old_patient_ids)).delete(synchronize_session=False)
        db.query(models.User).filter(models.User.id.in_(old_user_ids)).delete(synchronize_session=False)
        db.commit()
        print(f"Cleanup complete: removed {len(old_user_ids)} old @example.com patients and all linked records.\n")
    except Exception as e:
        db.rollback()
        print(f"Cleanup FAILED, rolled back. Error: {e}\n")
        raise

remaining_example = db.query(models.User).filter(models.User.email.like("patient%@example.com")).count()
remaining_gmail = db.query(models.User).filter(models.User.email.like("patient%@gmail.com")).count()
print(f"Verification: {remaining_example} @example.com patients remain (should be 0), "
      f"{remaining_gmail} @gmail.com patients remain intact.\n")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_or_create_user(email, role):
    user = db.query(models.User).filter(models.User.email == email).first()
    if user:
        return user, False
    user = models.User(email=email, password_hash=security.hash_password(PASSWORD), role=role)
    db.add(user)
    db.flush()
    return user, True


def next_or_same_weekday(start_date: date, weekday: int) -> date:
    days_ahead = (weekday - start_date.weekday()) % 7
    return start_date + timedelta(days=days_ahead)


def prev_or_same_weekday(start_date: date, weekday: int) -> date:
    days_behind = (start_date.weekday() - weekday) % 7
    return start_date - timedelta(days=days_behind)


# ---------------------------------------------------------------------------
# TASK 2 — Name-based gender classification
# ---------------------------------------------------------------------------

MALE_FIRST_NAMES = {
    "Ali", "Omar", "Hamza", "Yusuf", "Bilal", "Faisal", "Tariq",
    "Adeel", "Kamran", "Waqas", "Shahid", "Rizwan", "Junaid",
}
FEMALE_FIRST_NAMES = {
    "Zainab", "Mariam", "Khadija", "Amna", "Rabia", "Sadia",
    "Noor", "Sana", "Iqra", "Hira", "Lubna", "Sidra",
}

FIRST_NAMES = sorted(MALE_FIRST_NAMES | FEMALE_FIRST_NAMES)
LAST_NAMES = ["Khan", "Ahmed", "Malik", "Raza", "Hussain", "Siddiqui", "Qureshi", "Tariq", "Butt", "Shah"]
CITIES = ["Islamabad", "Rawalpindi", "Lahore", "Karachi", "Faisalabad", "Peshawar"]


def gender_for_first_name(first_name: str):
    if first_name in MALE_FIRST_NAMES:
        return "Male"
    if first_name in FEMALE_FIRST_NAMES:
        return "Female"
    return None


def pick_name_and_gender():
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    gender = gender_for_first_name(first)
    return f"{first} {last}", gender


# ---------------------------------------------------------------------------
# 1. Doctors
# ---------------------------------------------------------------------------

DOCTORS = [
    ("Dr. Ahmed Khan", "Cardiology", 8, 2500, [0, 2, 4]),
    ("Dr. Asif Shehzad", "Orthopedics", 12, 3000, [0, 2, 4]),
    ("Dr. Mehboob Ali", "Dermatology", 6, 1800, [1, 3, 5]),
    ("Dr. Sara Malik", "Physiotherapy", 5, 1500, [1, 3]),
    ("Dr. Imran Qureshi", "Neurology", 15, 4000, [0, 2]),
    ("Dr. Ayesha Siddiqui", "Gynecology", 10, 2800, [1, 3, 5]),
    ("Dr. Bilal Hussain", "ENT", 7, 2000, [0, 4]),
    ("Dr. Fatima Noor", "Pediatrics", 9, 2200, [0, 2, 4]),
    ("Dr. Usman Tariq", "Psychiatry", 11, 3200, [1, 3]),
    ("Dr. Hina Raza", "General Medicine", 4, 1500, [0, 1, 2, 3, 4]),
]

doctors = []
print("Creating doctors...")
for i, (name, spec, exp, fee, days) in enumerate(DOCTORS, start=1):
    email = f"doctor{i}@hospital.com"
    user, created = get_or_create_user(email, models.RoleEnum.doctor)
    doc = db.query(models.Doctor).filter(models.Doctor.user_id == user.id).first()
    if not doc:
        doc = models.Doctor(
            user_id=user.id, name=name, specialization=spec,
            experience_years=exp, bio=f"{name} is a specialist in {spec} with {exp} years of experience.",
            consultation_fee=fee, status="approved",
        )
        db.add(doc)
        db.flush()
    else:
        doc.status = "approved"
        doc.consultation_fee = fee

    for d in days:
        exists = db.query(models.DoctorAvailability).filter_by(doctor_id=doc.id, day_of_week=d).first()
        if not exists:
            db.add(models.DoctorAvailability(
                doctor_id=doc.id, day_of_week=d,
                start_time=time(9, 0), end_time=time(17, 0), slot_duration_minutes=30,
            ))
    doctors.append((doc, days))
    print(f"  {email} / {PASSWORD}  -> {name} ({spec})")

db.commit()

# ---------------------------------------------------------------------------
# 2. Receptionists
# ---------------------------------------------------------------------------

RECEPTIONISTS = [
    ("Ayesha Tariq", "0300-1234567"),
    ("Hassan Raza", "0321-2345678"),
    ("Sana Malik", "0333-3456789"),
]

receptionists = []
print("\nCreating receptionists...")
for i, (name, phone) in enumerate(RECEPTIONISTS, start=1):
    email = f"receptionist{i}@hospital.com"
    user, created = get_or_create_user(email, models.RoleEnum.receptionist)
    r = db.query(models.Receptionist).filter(models.Receptionist.user_id == user.id).first()
    if not r:
        r = models.Receptionist(user_id=user.id, name=name, phone=phone)
        db.add(r)
        db.flush()
    receptionists.append(r)
    print(f"  {email} / {PASSWORD}  -> {name}")

db.commit()

# ---------------------------------------------------------------------------
# 3. Admins
# ---------------------------------------------------------------------------

ADMINS = [("Hospital Admin One", "admin1@hospital.com"), ("Hospital Admin Two", "admin2@hospital.com")]

print("\nCreating admins...")
for name, email in ADMINS:
    user, created = get_or_create_user(email, models.RoleEnum.admin)
    a = db.query(models.Admin).filter(models.Admin.user_id == user.id).first()
    if not a:
        db.add(models.Admin(user_id=user.id, name=name))
    print(f"  {email} / {PASSWORD}  -> {name}")

db.commit()

# ---------------------------------------------------------------------------
# 4. Patients (new ones get a name-matched gender)
# ---------------------------------------------------------------------------

patients = []
print("\nCreating patients (gmail.com)...")
for i in range(1, 51):
    email = f"patient{i}@gmail.com"
    user, created = get_or_create_user(email, models.RoleEnum.patient)
    p = db.query(models.Patient).filter(models.Patient.user_id == user.id).first()
    if not p:
        name, gender = pick_name_and_gender()
        p = models.Patient(
            user_id=user.id,
            name=name,
            phone=f"03{random.randint(10,49)}-{random.randint(1000000,9999999)}",
            gender=gender,
            dob=date(random.randint(1960, 2015), random.randint(1, 12), random.randint(1, 28)),
            address=f"House {random.randint(1,200)}, Street {random.randint(1,40)}, {random.choice(CITIES)}",
        )
        db.add(p)
        db.flush()
    patients.append(p)

db.commit()
print(f"  patient1@gmail.com ... patient50@gmail.com / {PASSWORD}")

# ---------------------------------------------------------------------------
# TASK 2 (continued) — Fix gender on EXISTING patients by their first name
# ---------------------------------------------------------------------------

print("\nCorrecting gender on existing patient records based on first name...")
updated, skipped = 0, []

all_patients = db.query(models.Patient).all()
for p in all_patients:
    if not p.name:
        continue
    first_name = p.name.strip().split(" ")[0]
    correct_gender = gender_for_first_name(first_name)
    if correct_gender is None:
        skipped.append(f"{p.name} (id={p.id}) — first name not in known list, left unchanged")
        continue
    if p.gender != correct_gender:
        p.gender = correct_gender
        updated += 1

db.commit()
print(f"  Updated gender on {updated} existing patient(s).")
if skipped:
    print(f"  Skipped {len(skipped)} patient(s) whose first name could not be matched:")
    for line in skipped:
        print(f"    - {line}")

# ---------------------------------------------------------------------------
# 5. Appointments (+ payments, medical records, reviews)
# ---------------------------------------------------------------------------

print("\nCreating appointments, payments, medical records, and reviews...")

today = date.today()
used_slots = set()

REASONS = ["Routine checkup", "Follow-up visit", "Persistent headache", "Skin rash", "Back pain",
           "Chest discomfort", "Fever and cough", "Joint pain", "Annual physical", "Consultation"]

appointment_count = 0

def make_appointment(patient, doc, days_list, when, status):
    global appointment_count
    weekday = random.choice(days_list)
    if when == "past":
        appt_date = prev_or_same_weekday(today - timedelta(days=random.randint(1, 45)), weekday)
    else:
        appt_date = next_or_same_weekday(today + timedelta(days=random.randint(1, 20)), weekday)

    for _ in range(10):
        hour = random.choice(range(9, 17))
        minute = random.choice([0, 30])
        appt_time = time(hour, minute)
        key = (doc.id, appt_date, appt_time)
        if key not in used_slots:
            used_slots.add(key)
            break
    else:
        return None

    appt = models.Appointment(
        patient_id=patient.id, doctor_id=doc.id,
        appointment_date=appt_date, appointment_time=appt_time,
        status=status, reason=random.choice(REASONS),
    )
    db.add(appt)
    db.flush()
    appointment_count += 1

    if status in ("confirmed", "completed"):
        db.add(models.Payment(
            appointment_id=appt.id, amount=float(doc.consultation_fee),
            method=random.choice(["cash", "card", "bank_transfer"]),
            status="verified", verified_by=random.choice(receptionists).id,
        ))

    if status == "completed":
        db.add(models.MedicalRecord(
            patient_id=patient.id, doctor_id=doc.id, appointment_id=appt.id,
            diagnosis=random.choice(["Mild viral infection", "Muscular strain", "Seasonal allergy",
                                      "Hypertension (controlled)", "Minor skin irritation", "No major concerns found"]),
            prescription=random.choice(["Paracetamol 500mg, twice daily for 3 days",
                                         "Ibuprofen as needed for pain",
                                         "Topical cream, apply twice daily",
                                         "Rest and hydration advised"]),
            notes="Patient advised to follow up if symptoms persist beyond a week.",
        ))
        if random.random() < 0.6:
            db.add(models.Review(
                patient_id=patient.id, doctor_id=doc.id, appointment_id=appt.id,
                rating=random.choice([3, 4, 4, 5, 5, 5]),
                comment=random.choice([
                    "Very professional and explained everything clearly.",
                    "Good experience, short waiting time.",
                    "Doctor was attentive and helpful.",
                    "Satisfied with the consultation.",
                    "Would recommend to others.",
                ]),
            ))

    return appt


# Only generate fresh appointments for patients who don't already have any
# (keeps the script safe to re-run without piling up more and more bookings)
for patient in patients:
    existing_count = db.query(models.Appointment).filter(models.Appointment.patient_id == patient.id).count()
    if existing_count > 0:
        continue
    num_appts = random.randint(1, 4)
    for _ in range(num_appts):
        doc, days_list = random.choice(doctors)
        status = random.choices(
            ["completed", "confirmed", "pending", "cancelled"],
            weights=[50, 20, 20, 10],
        )[0]
        when = "past" if status in ("completed", "cancelled") else random.choice(["past", "future"])
        make_appointment(patient, doc, days_list, when, status)

db.commit()
print(f"  {appointment_count} new appointments created (with matching payments, records, and reviews)")

# ---------------------------------------------------------------------------
# 6. Attendance (doctors + receptionists, last 10 working days)
# ---------------------------------------------------------------------------

print("\nCreating attendance records...")
staff_users = [d.user_id for d, _ in doctors] + [r.user_id for r in receptionists]

count = 0
for staff_user_id in staff_users:
    for i in range(1, 11):
        d = today - timedelta(days=i)
        if d.weekday() == 6:
            continue
        existing = db.query(models.StaffAttendance).filter_by(staff_user_id=staff_user_id, date=d).first()
        if existing:
            continue
        check_in_dt = datetime.combine(d, time(9, random.randint(0, 20))) - timedelta(hours=5)
        check_out_dt = datetime.combine(d, time(17, random.randint(0, 30))) - timedelta(hours=5)
        db.add(models.StaffAttendance(
            staff_user_id=staff_user_id, date=d,
            check_in=check_in_dt, check_out=check_out_dt, status="present",
        ))
        count += 1

db.commit()
print(f"  {count} attendance records created")

# ---------------------------------------------------------------------------
# 7. Notifications for confirmed/cancelled appointments
# ---------------------------------------------------------------------------

print("\nCreating notifications...")
notif_count = 0
relevant = db.query(models.Appointment).filter(
    models.Appointment.status.in_([models.AppointmentStatus.confirmed, models.AppointmentStatus.cancelled])
).all()
for appt in relevant:
    patient = db.query(models.Patient).filter(models.Patient.id == appt.patient_id).first()
    if not patient:
        continue
    verb = "confirmed" if appt.status == models.AppointmentStatus.confirmed else "cancelled"
    exists = db.query(models.Notification).filter(
        models.Notification.user_id == patient.user_id,
        models.Notification.message.like(f"%{appt.appointment_date}%{verb}%"),
    ).first()
    if not exists:
        db.add(models.Notification(
            user_id=patient.user_id,
            message=f"Your appointment on {appt.appointment_date} at {appt.appointment_time} has been {verb}.",
            is_read=random.choice([True, False]),
        ))
        notif_count += 1

db.commit()
print(f"  {notif_count} notifications created")

db.close()
print("\nDone. All demo accounts use the password:", PASSWORD)