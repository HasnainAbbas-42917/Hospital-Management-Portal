from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas, security

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
        db.add(models.Patient(user_id=user.id, name=user_in.name))
    elif user_in.role == models.RoleEnum.doctor:
        db.add(models.Doctor(user_id=user.id, name=user_in.name))
    elif user_in.role == models.RoleEnum.admin:
        db.add(models.Admin(user_id=user.id, name=user_in.name))

    db.commit()

    token = security.create_access_token({"sub": str(user.id), "role": user.role})
    return schemas.Token(access_token=token, role=user.role)


@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")

    token = security.create_access_token({"sub": str(user.id), "role": user.role})
    return schemas.Token(access_token=token, role=user.role)