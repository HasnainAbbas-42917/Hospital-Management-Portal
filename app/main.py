from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.database import Base, engine
from app.routers import auth, patients, doctors, receptionist, admin, reviews, attendance, notifications
from app import routes_pages

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Hospital Appointment & Management Portal")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(auth.router)
app.include_router(patients.router)
app.include_router(doctors.router)
app.include_router(receptionist.router)
app.include_router(admin.router)
app.include_router(reviews.router)
app.include_router(attendance.router)
app.include_router(notifications.router)
app.include_router(routes_pages.router)