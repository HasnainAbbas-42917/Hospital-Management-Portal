from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List
from datetime import date, time, datetime
from app.models import RoleEnum, AppointmentStatus, PaymentStatus


# ---------- Auth ----------
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: RoleEnum
    name: str
    phone: Optional[str] = None
    dob: Optional[date] = None
    gender: Optional[str] = None
    address: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: RoleEnum


# ---------- Doctor ----------
class DoctorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    specialization: Optional[str]
    experience_years: int
    bio: Optional[str]
    consultation_fee: float
    status: str


class PublicDoctorScheduleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    day_of_week: int
    start_time: time
    end_time: time
    slot_duration_minutes: int


class PublicDoctorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    specialization: Optional[str]
    experience_years: int
    bio: Optional[str]
    consultation_fee: float
    status: str
    availability: str
    schedule: List[PublicDoctorScheduleOut]


# ---------- Patient ----------
class PatientOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    phone: Optional[str]
    dob: Optional[date]
    gender: Optional[str]
    address: Optional[str]

class PatientProfileUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    dob: Optional[date] = None
    gender: Optional[str] = None
    address: Optional[str] = None

class PatientProfileCreate(BaseModel):
    name: str
    phone: Optional[str] = None
    dob: Optional[date] = None
    gender: Optional[str] = None
    address: Optional[str] = None

# ---------- Appointment ----------
class AppointmentCreate(BaseModel):
    doctor_id: int
    appointment_date: date
    appointment_time: time
    reason: Optional[str] = None


class AppointmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    doctor_id: int
    patient_id: int
    appointment_date: date
    appointment_time: time
    status: AppointmentStatus
    reason: Optional[str]

# ---------- Doctor Availability ----------
class DoctorAvailabilityCreate(BaseModel):
    day_of_week: int   # 0 = Monday ... 6 = Sunday
    start_time: time
    end_time: time
    slot_duration_minutes: int = 30


class DoctorAvailabilityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    day_of_week: int
    start_time: time
    end_time: time
    slot_duration_minutes: int


# ---------- Medical Records ----------
class MedicalRecordCreate(BaseModel):
    diagnosis: Optional[str] = None
    prescription: Optional[str] = None
    notes: Optional[str] = None


class MedicalRecordOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    diagnosis: Optional[str]
    prescription: Optional[str]
    notes: Optional[str]
    created_at: datetime


# ---------- Appointment status update ----------
class AppointmentStatusUpdate(BaseModel):
    status: AppointmentStatus


# ---------- Review ----------
class ReviewCreate(BaseModel):
    appointment_id: int
    rating: int
    comment: Optional[str] = None


class ReviewOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    rating: int
    comment: Optional[str]
    patient_id: int

# ---------- Payment ----------
class PaymentVerify(BaseModel):
    amount: float
    method: str
    status: PaymentStatus

# ---------- Attendance ----------
class AttendanceCheckIn(BaseModel):
    pass  # no input needed; check-in time is set automatically


class AttendanceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    date: date
    check_in: Optional[datetime]
    check_out: Optional[datetime]
    status: str

# ---------- Notifications ----------
class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    message: str
    is_read: bool
    created_at: datetime

# ---------- Doctor Profile Update ----------
class DoctorProfileUpdate(BaseModel):
    name: Optional[str] = None
    specialization: Optional[str] = None
    experience_years: Optional[int] = None
    bio: Optional[str] = None
    requested_schedule_note: Optional[str] = None

# ---------- Admin: Doctor Fee & Receptionist Creation ----------
class DoctorFeeUpdate(BaseModel):
    consultation_fee: float


class ReceptionistCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    phone: Optional[str] = None


class ReceptionistProfileUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None

    # ---------- Password reset ----------
class ForgotPasswordRequest(BaseModel):
    email: EmailStr
    phone: str
    dob: date
    new_password: str


class AdminPasswordReset(BaseModel):
    new_password: str