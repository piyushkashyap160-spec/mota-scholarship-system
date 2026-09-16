from typing import Dict, Any, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, Application
from ..auth import get_current_user
from ..integrations.digilocker import get_sandbox_profiles, fetch_issued_documents, get_auth_url
from ..integrations.aadhaar_ekyc import send_aadhaar_otp, verify_aadhaar_otp
from ..integrations.pfms_tracker import get_disbursement_tracker, log_disbursement_grievance

router = APIRouter(prefix="/api/integrations", tags=["India Stack & PFMS Integrations"])

# Schemas
class DigiLockerFetchRequest(BaseModel):
    profile_id: str = "jharkhand_birsa"

class AadhaarOtpRequest(BaseModel):
    aadhaar_number: str

class AadhaarVerifyRequest(BaseModel):
    txn_id: str
    otp: str
    aadhaar_number: str
    applicant_name: Optional[str] = None

class GrievanceRequest(BaseModel):
    grievance_type: str
    description: str

# 1. DigiLocker Endpoints
@router.get("/digilocker/profiles")
def list_digilocker_sandbox_profiles():
    """List pre-configured test profiles for 1-click DigiLocker sandbox testing."""
    return get_sandbox_profiles()

@router.post("/digilocker/fetch")
def fetch_digilocker_documents(payload: DigiLockerFetchRequest):
    """Fetches digitally signed, issuer-verified documents and autofill data from DigiLocker."""
    try:
        return fetch_issued_documents(payload.profile_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/digilocker/auth-url")
def get_digilocker_oauth_url(redirect_uri: str = Query("http://localhost:5173/digilocker-callback")):
    """Generates OAuth2 authorization URL for production API Setu gateway."""
    return {"auth_url": get_auth_url(redirect_uri)}

# 2. Aadhaar e-KYC Endpoints
@router.post("/aadhaar/send-otp")
def generate_aadhaar_otp(payload: AadhaarOtpRequest):
    """Simulates sending an OTP to the UIDAI-registered mobile number for any 12-digit Aadhaar."""
    try:
        return send_aadhaar_otp(payload.aadhaar_number)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

@router.post("/aadhaar/verify-otp")
def confirm_aadhaar_ekyc(
    payload: AadhaarVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verifies the 6-digit Aadhaar OTP (test OTP: 123456) and returns certified demographic identity."""
    try:
        res = verify_aadhaar_otp(
            txn_id=payload.txn_id,
            otp=payload.otp,
            aadhaar_number=payload.aadhaar_number,
            applicant_name=payload.applicant_name or current_user.full_name
        )
        return res
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

# 3. PFMS Disbursement Tracker Endpoints
@router.get("/pfms/{app_id}")
def get_application_pfms_tracking(
    app_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Provides real-time PFMS DBT stages, NPCI account validation, and instalment schedule."""
    app = db.query(Application).filter(Application.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    scheme_code = app.scheme.code if app.scheme else "NFST"
    return get_disbursement_tracker(app.id, app.status, scheme_code=scheme_code)

@router.post("/pfms/{app_id}/grievance")
def create_disbursement_grievance(
    app_id: int,
    payload: GrievanceRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Logs a formal PFMS/DBT delayed disbursement grievance with tracking token."""
    app = db.query(Application).filter(Application.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    return log_disbursement_grievance(
        application_id=app.id,
        applicant_name=current_user.full_name,
        grievance_type=payload.grievance_type,
        description=payload.description
    )
