from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas, security
import time as _time
from collections import defaultdict
from sqlalchemy import func

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=schemas.Token)
def register(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    if user_in.role == models.RoleEnum.receptionist:
        raise HTTPException(
            status_code=403,
            detail="Receptionist accounts can only be created by an administrator."
        )

    existing = db.query(models.User).filter(models.User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = models.User(
        email=user_in.email,
        password_hash=security.hash_password(user_in.password),
        role=user_in.role,
    )
    db.add(user)
    db.flush()

    if user_in.role == models.RoleEnum.patient:
        db.add(models.Patient(
            user_id=user.id,
            name=user_in.name,
            phone=user_in.phone,
            dob=user_in.dob,
            gender=user_in.gender,
            address=user_in.address,
        ))
    elif user_in.role == models.RoleEnum.doctor:
        db.add(models.Doctor(user_id=user.id, name=user_in.name))
    elif user_in.role == models.RoleEnum.admin:
        db.add(models.Admin(user_id=user.id, name=user_in.name))

    db.commit()

    token = security.create_access_token({"sub": str(user.id), "role": user.role.value})
    return schemas.Token(access_token=token, role=user.role)


@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")

    token = security.create_access_token({"sub": str(user.id), "role": user.role.value})
    return schemas.Token(access_token=token, role=user.role)

# ---------- Forgot password (patients only, identity-verified) ----------
_reset_attempts = defaultdict(list)
MAX_RESET_ATTEMPTS = 5
RESET_WINDOW_SECONDS = 15 * 60


def _too_many_attempts(key: str) -> bool:
    now = _time.time()
    recent = [t for t in _reset_attempts[key] if now - t < RESET_WINDOW_SECONDS]
    _reset_attempts[key] = recent
    return len(recent) >= MAX_RESET_ATTEMPTS


def _digits(value) -> str:
    return "".join(ch for ch in (value or "") if ch.isdigit())


@router.post("/forgot-password")
def forgot_password(data: schemas.ForgotPasswordRequest, db: Session = Depends(get_db)):
    key = data.email.lower()

    if _too_many_attempts(key):
        raise HTTPException(
            status_code=429,
            detail="Too many attempts. Please try again in 15 minutes or contact the hospital administration.",
        )

    if len(data.new_password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters.")

    user = db.query(models.User).filter(func.lower(models.User.email) == key).first()

    patient = None
    if user and user.is_active and getattr(user.role, "value", user.role) == "patient":
        patient = db.query(models.Patient).filter(models.Patient.user_id == user.id).first()

    # Compare last 10 digits so "0300-1234567" and "+92 300 1234567" both match
    verified = bool(
        patient
        and patient.phone
        and patient.dob
        and _digits(patient.phone)[-10:] == _digits(data.phone)[-10:]
        and patient.dob == data.dob
    )

    if not verified:
        _reset_attempts[key].append(_time.time())
        raise HTTPException(
            status_code=400,
            detail="We could not verify these details. Please check them or contact the hospital administration.",
        )

    user.password_hash = security.hash_password(data.new_password)
    db.commit()
    _reset_attempts.pop(key, None)
    return {"detail": "Password updated. You can now log in with your new password."}