import unittest
from datetime import time

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import models
from app.database import Base
from app.routers.patients import search_doctors


class PublicDoctorScheduleTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=self.engine)
        self.db = sessionmaker(bind=self.engine)()

        doctor = models.Doctor(
            id=1,
            user_id=1,
            name="Dr. Ayesha Khan",
            specialization="Cardiology",
            experience_years=8,
            bio="Cardiology specialist",
            consultation_fee=1500,
            status="approved",
        )
        self.db.add(doctor)
        self.db.add(
            models.DoctorAvailability(
                doctor_id=1,
                day_of_week=0,
                start_time=time(9, 0),
                end_time=time(17, 0),
                slot_duration_minutes=30,
            )
        )
        self.db.commit()

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def test_public_search_includes_backend_schedule_data(self):
        doctors = search_doctors(db=self.db)

        self.assertEqual(len(doctors), 1)
        public_doctor = doctors[0]
        self.assertEqual(public_doctor["schedule"][0]["day_of_week"], 0)
        self.assertEqual(public_doctor["schedule"][0]["start_time"], "09:00:00")
        self.assertEqual(public_doctor["schedule"][0]["end_time"], "17:00:00")
        self.assertEqual(public_doctor["schedule"][0]["slot_duration_minutes"], 30)
        self.assertEqual(public_doctor["availability"], "available")


if __name__ == "__main__":
    unittest.main()
