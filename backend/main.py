from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.auth import router as auth_router
from api.health import router as health_router
from api.users import router as users_router
from api.documents import router as documents_router
from api.medications import router as medications_router
from api.reminders import router as reminder_router
from api.verification import router as verification_router
from api.monitoring import router as monitoring_router
from api.analytics import router as analytics_router
from services.doctor_monitoring import start_doctor_monitoring_daemon


app = FastAPI(
    title="MediVerify AI API",
    version="0.1.0",
)

@app.on_event("startup")
def startup_event():
    start_doctor_monitoring_daemon()


# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health Routes
app.include_router(health_router)

# API Routes
app.include_router(auth_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(documents_router, prefix="/api")
app.include_router(medications_router, prefix="/api")
app.include_router(reminder_router, prefix="/api")
app.include_router(verification_router, prefix="/api")
app.include_router(monitoring_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")


@app.get("/")
def root():
    return {
        "status": "running",
        "message": "MediVerify AI API is running successfully"
    }