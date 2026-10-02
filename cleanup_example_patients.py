"""Preview or remove the legacy patient1@example.com through patient50@example.com data.

Run from the project root with the project's virtual environment active:
    python cleanup_example_patients.py
    python cleanup_example_patients.py --apply

Preview is read-only and is the default. Applying requires typing the exact
confirmation shown after the affected rows have been listed.
"""

import argparse

from sqlalchemy import or_

from app import models
from app.database import SessionLocal


def collect_targets(session):
    target_emails = [f"patient{number}@example.com" for number in range(1, 51)]
    users = (
        session.query(models.User)
        .filter(
            models.User.email.in_(target_emails),
            models.User.role == models.RoleEnum.patient,
        )
        .order_by(models.User.email)
        .all()
    )
    user_ids = [user.id for user in users]

    patients = (
        session.query(models.Patient)
        .filter(models.Patient.user_id.in_(user_ids))
        .order_by(models.Patient.id)
        .all()
    )
    patient_ids = [patient.id for patient in patients]

    appointments = (
        session.query(models.Appointment)
        .filter(models.Appointment.patient_id.in_(patient_ids))
        .order_by(models.Appointment.id)
        .all()
    )
    appointment_ids = [appointment.id for appointment in appointments]

    payments = (
        session.query(models.Payment)
        .filter(models.Payment.appointment_id.in_(appointment_ids))
        .order_by(models.Payment.id)
        .all()
    )
    medical_records = (
        session.query(models.MedicalRecord)
        .filter(
            or_(
                models.MedicalRecord.patient_id.in_(patient_ids),
                models.MedicalRecord.appointment_id.in_(appointment_ids),
            )
        )
        .order_by(models.MedicalRecord.id)
        .all()
    )
    reviews = (
        session.query(models.Review)
        .filter(
            or_(
                models.Review.patient_id.in_(patient_ids),
                models.Review.appointment_id.in_(appointment_ids),
            )
        )
        .order_by(models.Review.id)
        .all()
    )
    notifications = (
        session.query(models.Notification)
        .filter(models.Notification.user_id.in_(user_ids))
        .order_by(models.Notification.id)
        .all()
    )
    attendance = (
        session.query(models.StaffAttendance)
        .filter(models.StaffAttendance.staff_user_id.in_(user_ids))
        .order_by(models.StaffAttendance.id)
        .all()
    )

    return {
        "users": users,
        "patients": patients,
        "appointments": appointments,
        "payments": payments,
        "medical_records": medical_records,
        "reviews": reviews,
        "notifications": notifications,
        "attendance": attendance,
    }


def show_preview(targets, applying):
    print("CLEANUP PREVIEW (transaction open)" if applying else "READ-ONLY CLEANUP PREVIEW")
    print("Target: patient1@example.com through patient50@example.com, patient role only")
    print("Gmail accounts and all non-matching accounts are excluded.\n")

    for user in targets["users"]:
        patient_id = user.patient_profile.id if user.patient_profile else "none"
        print(f"User: id={user.id}, email={user.email}, patient_id={patient_id}")

    row_specs = (
        ("patients", "Patient", lambda row: f"id={row.id}, user_id={row.user_id}"),
        ("appointments", "Appointment", lambda row: f"id={row.id}, patient_id={row.patient_id}"),
        ("payments", "Payment", lambda row: f"id={row.id}, appointment_id={row.appointment_id}"),
        (
            "medical_records",
            "MedicalRecord",
            lambda row: f"id={row.id}, patient_id={row.patient_id}, appointment_id={row.appointment_id}",
        ),
        (
            "reviews",
            "Review",
            lambda row: f"id={row.id}, patient_id={row.patient_id}, appointment_id={row.appointment_id}",
        ),
        ("notifications", "Notification", lambda row: f"id={row.id}, user_id={row.user_id}"),
        ("attendance", "StaffAttendance", lambda row: f"id={row.id}, staff_user_id={row.staff_user_id}"),
    )

    print("\nRows scheduled for deletion:")
    for key, label, describe in row_specs:
        rows = targets[key]
        print(f"{label}: {len(rows)}")
        for row in rows:
            print(f"  {describe(row)}")

    print("\nRecord counts:")
    for key, label, _ in row_specs:
        print(f"  {label}: {len(targets[key])}")
    print(f"  User: {len(targets['users'])}")


def delete_targets(session, targets):
    deletions = (
        (models.Notification, targets["notifications"]),
        (models.StaffAttendance, targets["attendance"]),
        (models.Payment, targets["payments"]),
        (models.MedicalRecord, targets["medical_records"]),
        (models.Review, targets["reviews"]),
        (models.Appointment, targets["appointments"]),
        (models.Patient, targets["patients"]),
        (models.User, targets["users"]),
    )

    affected = {}
    for model, rows in deletions:
        row_ids = [row.id for row in rows]
        affected[model.__name__] = (
            session.query(model)
            .filter(model.id.in_(row_ids))
            .delete(synchronize_session=False)
        )
    return affected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="show the preview, then allow deletion after exact typed confirmation",
    )
    options = parser.parse_args()

    with SessionLocal() as session:
        if not options.apply:
            targets = collect_targets(session)
            show_preview(targets, applying=False)
            session.rollback()
            print("\nNo changes made. Re-run with --apply to review and confirm deletion.")
            return

        with session.begin():
            targets = collect_targets(session)
            show_preview(targets, applying=True)
            expected = f"DELETE {len(targets['users'])} EXAMPLE.COM PATIENT ACCOUNTS"
            print(f"\nTo delete these rows and commit, type exactly:\n{expected}")
            if input("> ").strip() != expected:
                print("Confirmation did not match. No changes made; nothing was committed.")
                return

            affected = delete_targets(session, targets)
            staged_total = sum(affected.values())
            print("\nStaged deletion counts (not committed):")
            for model_name, count in affected.items():
                print(f"  {model_name}: {count}")
            print(f"  Total: {staged_total}")

            commit_confirmation = f"COMMIT {staged_total} DELETIONS"
            print(f"\nTo commit these staged deletions, type exactly:\n{commit_confirmation}")
            if input("> ").strip() != commit_confirmation:
                session.rollback()
                print("Commit confirmation did not match. Transaction rolled back; no changes made.")
                return

        print("\nCommitted deletion counts:")
        for model_name, count in affected.items():
            print(f"  {model_name}: {count}")


if __name__ == "__main__":
    main()