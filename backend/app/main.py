from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.exports import router as export_router
from app.routes.analytics import router as analytics_router
from app.routes.patients import router as patient_router
from app.routes.auth_routes import router as auth_router
from app.database import Base, engine
from app import models
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="PatientFlow API",
    description="Patient Admission Management System",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    patient_router,
    prefix="/api/v1/patients",
    tags=["Patients"]
)

app.include_router(
    analytics_router,
    prefix="/api/v1/analytics",
    tags=["Analytics"]
)

app.include_router(
    export_router,
    prefix="/api/v1/exports",
    tags=["Exports"]
)

app.include_router(
    auth_router,
    prefix="/api/v1/auth",
    tags=["Authentication"]
)

@app.get("/")
def home():
    return {"message": "PatientFlow API is running"}

@app.get("/api/v1/health")
def health():
    return {"status": "healthy"}