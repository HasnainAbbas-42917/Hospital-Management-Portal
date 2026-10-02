"""Preview or correct gender fields using patient first names.

Run from the project root:
    python fix_patient_gender.py
    python fix_patient_gender.py --apply
"""

import argparse

from app.database import SessionLocal
from app.models import Patient


MALE_FIRST_NAMES = {
    "ali",
    "omar",
    "hamza",
    "yusuf",
    "bilal",
    "faisal",
    "tariq",
    "adeel",
    "kamran",
    "waqas",
    "shahid",
    "rizwan",
    "junaid",
}

FEMALE_FIRST_NAMES = {
    "zainab",
    "mariam",
    "khadija",
    "amna",
    "rabia",
    "sadia",
    "sana",
    "iqra",
    "hira",
    "lubna",
    "sidra",
}


def classify_patients(patients):
    changes = []
    skipped = []
    already_correct = []

    for patient in patients:
        first_name = patient.name.strip().split(maxsplit=1)[0].casefold() if patient.name.strip() else ""
        if first_name in MALE_FIRST_NAMES:
            expected_gender = "Male"
        elif first_name in FEMALE_FIRST_NAMES:
            expected_gender = "Female"
        else:
            skipped.append((patient, first_name or "(missing first name)"))
            continue

        if patient.gender == expected_gender:
            already_correct.append((patient, expected_gender))
        else:
            changes.append((patient, expected_gender))

    return changes, skipped, already_correct


def show_plan(changes, skipped, already_correct):
    male_changes = [(patient, gender) for patient, gender in changes if gender == "Male"]
    female_changes = [(patient, gender) for patient, gender in changes if gender == "Female"]

    print("Patients to change to Male:", len(male_changes))
    for patient, _ in male_changes:
        print(f"  id={patient.id}, name={patient.name}, current_gender={patient.gender!r}")

    print("Patients to change to Female:", len(female_changes))
    for patient, _ in female_changes:
        print(f"  id={patient.id}, name={patient.name}, current_gender={patient.gender!r}")

    print("Patients skipped (first name not confidently classified):", len(skipped))
    for patient, first_name in skipped:
        print(f"  id={patient.id}, name={patient.name!r}, extracted_first_name={first_name!r}")

    print("Patients already correct:", len(already_correct))
    for patient, gender in already_correct:
        print(f"  id={patient.id}, name={patient.name}, gender={gender}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="stage gender-only updates after preview and commit only after verification",
    )
    options = parser.parse_args()

    with SessionLocal() as session:
        with session.begin():
            patients = session.query(Patient).order_by(Patient.id).all()
            changes, skipped, already_correct = classify_patients(patients)
            show_plan(changes, skipped, already_correct)

            if not options.apply:
                print("\nRead-only preview; no changes made. Re-run with --apply to proceed.")
                return

            update_confirmation = f"UPDATE {len(changes)} PATIENT GENDERS"
            print(f"\nTo stage these gender-only updates, type exactly:\n{update_confirmation}")
            if input("> ").strip() != update_confirmation:
                print("Confirmation did not match. No changes made; nothing was committed.")
                return

            staged_changes = []
            for patient, expected_gender in changes:
                old_gender = patient.gender
                patient.gender = expected_gender
                staged_changes.append((patient.id, patient.name, old_gender, expected_gender))

            session.flush()
            verified = {
                patient_id: gender
                for patient_id, gender in (
                    session.query(Patient.id, Patient.gender)
                    .filter(Patient.id.in_([item[0] for item in staged_changes]))
                    .all()
                )
            }
            if len(verified) != len(staged_changes) or any(
                verified.get(patient_id) != expected_gender
                for patient_id, _, _, expected_gender in staged_changes
            ):
                raise RuntimeError("Staged gender verification failed; transaction will roll back.")

            male_count = sum(gender == "Male" for _, _, _, gender in staged_changes)
            female_count = sum(gender == "Female" for _, _, _, gender in staged_changes)
            print("\nStaged updates verified; not committed:")
            print(f"  Male: {male_count}")
            print(f"  Female: {female_count}")
            for patient_id, name, old_gender, new_gender in staged_changes:
                print(f"  id={patient_id}, name={name}, gender={old_gender!r} -> {new_gender}")

            commit_confirmation = f"COMMIT {len(staged_changes)} GENDER UPDATES"
            print(f"\nTo commit these verified changes, type exactly:\n{commit_confirmation}")
            if input("> ").strip() != commit_confirmation:
                session.rollback()
                print("Commit confirmation did not match. Transaction rolled back; no changes made.")
                return

        print("\nCommitted patient gender updates:")
        print(f"  Male: {male_count}")
        print(f"  Female: {female_count}")
        for patient_id, name, old_gender, new_gender in staged_changes:
            print(f"  id={patient_id}, name={name}, gender={old_gender!r} -> {new_gender}")


if __name__ == "__main__":
    main()