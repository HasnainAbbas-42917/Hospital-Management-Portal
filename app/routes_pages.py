from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/login", response_class=HTMLResponse, include_in_schema=False)
def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html", {})


@router.get("/register", response_class=HTMLResponse, include_in_schema=False)
def register_page(request: Request):
    return templates.TemplateResponse(request, "register.html", {})


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
def root_redirect(request: Request):
    return templates.TemplateResponse(request, "login.html", {})


@router.get("/patient/dashboard", response_class=HTMLResponse, include_in_schema=False)
def patient_dashboard(request: Request):
    return templates.TemplateResponse(request, "patient/dashboard.html", {"active": "dashboard"})


@router.get("/patient/appointments", response_class=HTMLResponse, include_in_schema=False)
def patient_appointments(request: Request):
    return templates.TemplateResponse(request, "patient/appointments.html", {"active": "appointments"})


@router.get("/doctor/dashboard", response_class=HTMLResponse, include_in_schema=False)
def doctor_dashboard(request: Request):
    return templates.TemplateResponse(request, "doctor/appointments.html", {"active": "appointments"})


@router.get("/doctor/profile", response_class=HTMLResponse, include_in_schema=False)
def doctor_profile(request: Request):
    return templates.TemplateResponse(request, "doctor/profile.html", {"active": "profile"})


@router.get("/doctor/attendance", response_class=HTMLResponse, include_in_schema=False)
def doctor_attendance(request: Request):
    return templates.TemplateResponse(request, "doctor/attendance.html", {"active": "attendance"})


@router.get("/receptionist/dashboard", response_class=HTMLResponse, include_in_schema=False)
def receptionist_dashboard(request: Request):
    return templates.TemplateResponse(request, "receptionist/appointments.html", {"active": "appointments"})


@router.get("/receptionist/attendance", response_class=HTMLResponse, include_in_schema=False)
def receptionist_attendance(request: Request):
    return templates.TemplateResponse(request, "receptionist/attendance.html", {"active": "attendance"})


@router.get("/admin/dashboard", response_class=HTMLResponse, include_in_schema=False)
def admin_overview(request: Request):
    return templates.TemplateResponse(request, "admin/overview.html", {"active": "overview"})


@router.get("/admin/manage-doctors", response_class=HTMLResponse, include_in_schema=False)
def admin_doctors(request: Request):
    return templates.TemplateResponse(request, "admin/doctors.html", {"active": "doctors"})


@router.get("/admin/manage-receptionists", response_class=HTMLResponse, include_in_schema=False)
def admin_receptionists(request: Request):
    return templates.TemplateResponse(request, "admin/receptionists.html", {"active": "receptionists"})


@router.get("/admin/manage-patients", response_class=HTMLResponse, include_in_schema=False)
def admin_patients(request: Request):
    return templates.TemplateResponse(request, "admin/patients.html", {"active": "patients"})


@router.get("/admin/manage-appointments", response_class=HTMLResponse, include_in_schema=False)
def admin_appointments(request: Request):
    return templates.TemplateResponse(request, "admin/appointments.html", {"active": "appointments"})


@router.get("/admin/manage-attendance", response_class=HTMLResponse, include_in_schema=False)
def admin_attendance(request: Request):
    return templates.TemplateResponse(request, "admin/attendance.html", {"active": "attendance"})


@router.get("/admin/manage-reviews", response_class=HTMLResponse, include_in_schema=False)
def admin_reviews(request: Request):
    return templates.TemplateResponse(request, "admin/reviews.html", {"active": "reviews"})

@router.get("/patient/profile", response_class=HTMLResponse, include_in_schema=False)
def patient_profile(request: Request):
    return templates.TemplateResponse(request, "patient/profile.html", {"active": "profile"})


@router.get("/receptionist/profile", response_class=HTMLResponse, include_in_schema=False)
def receptionist_profile(request: Request):
    return templates.TemplateResponse(request, "receptionist/profile.html", {"active": "profile"})

@router.get("/doctor/patients", response_class=HTMLResponse, include_in_schema=False)
def doctor_patients(request: Request):
    return templates.TemplateResponse(request, "doctor/patients.html", {"active": "patients"})

@router.get("/patient/records", response_class=HTMLResponse, include_in_schema=False)
def patient_records(request: Request):
    return templates.TemplateResponse(request, "patient/records.html", {"active": "records"})