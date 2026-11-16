from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models
from app.api.routes import auth as auth_routes
from app.api.routes import patient as patient_routes
from app.api.routes import medical_history as medical_history_routes
from app.api.routes import medical_reports as medical_reports_routes
from app.api.routes import health_timeline as health_timeline_routes
from app.database import Base, engine


app = FastAPI(
    title="MedIntel API",
    version="1.0.0",
)


# ============================================================
# DATABASE TABLE CREATION
# ============================================================

Base.metadata.create_all(bind=engine)


# ============================================================
# CORS CONFIGURATION
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1|0\.0\.0\.0):517[3-4]",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# AUTHENTICATION ROUTES
# ============================================================

app.include_router(
    auth_routes.router,
    prefix="/api/auth",
    tags=["Authentication"],
)


# ============================================================
# PATIENT HEALTH RECORD ROUTES
# ============================================================

app.include_router(
    patient_routes.router,
    prefix="/api/patient",
    tags=["Patient"],
)


# ============================================================
# MEDICAL HISTORY ROUTES
# ============================================================

app.include_router(
    medical_history_routes.router,
    prefix="/api/patient",
    tags=["Medical History"],
)


# ============================================================
# MEDICAL REPORT ROUTES
# ============================================================

app.include_router(
    medical_reports_routes.router,
    prefix="/api/patient",
    tags=["Medical Reports"],
)


# ============================================================
# HEALTH TIMELINE ROUTES
# ============================================================

app.include_router(
    health_timeline_routes.router,
    prefix="/api/patient",
    tags=["Health Timeline"],
)


# ============================================================
# GENERAL HEALTH CHECK
# ============================================================

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "medintel-backend",
    }