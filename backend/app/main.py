from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from .config import UPLOAD_DIR
from .database import engine, Base, SessionLocal
from .seed_data import seed_database
from .routes import auth_routes, scheme_routes, document_routes, application_routes, admin_routes, integration_routes

# Create all database tables
Base.metadata.create_all(bind=engine)

# Auto seed database on startup
db = SessionLocal()
try:
    seed_database(db)
finally:
    db.close()

app = FastAPI(
    title="MoTA Scholarship & Fellowship Management System",
    description="SIH 26239: Comprehensive digital scholarship lifecycle & AI-assisted document verification platform for Scheduled Tribe (ST) students.",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static uploads
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Include Routers
app.include_router(auth_routes.router)
app.include_router(scheme_routes.router)
app.include_router(document_routes.router)
app.include_router(application_routes.router)
app.include_router(admin_routes.router)
app.include_router(integration_routes.router)

@app.get("/")
def root():
    return {
        "portal": "MoTA Scholarship & Fellowship Management System",
        "ministry": "Ministry of Tribal Affairs, Government of India",
        "problem_statement": "SIH-2024 / SIH-26239",
        "status": "Operational",
        "api_docs": "/docs"
    }

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "service": "mota-backend-api"}
