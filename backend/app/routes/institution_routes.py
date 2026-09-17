from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, Scheme, Application, Document, Deficiency, ActivityLog, EnrollmentVerification
from ..schemas import ApplicationOut, ApplicationDetailOut, EnrollmentVerificationRequest, EnrollmentVerificationOut
from ..auth import get_current_institution_officer
from ..audit import log_action
from ..notifications import notification_service

router = APIRouter(prefix="/api/institution", tags=["Institution Nodal Officer"])

def _matches_institution(officer_inst: str, app_inst: str) -> bool:
    if not officer_inst or not app_inst:
        return False
    o = officer_inst.strip().lower()
    a = app_inst.strip().lower()
    if o in a or a in o:
        return True
    
    # Common acronym normalization
    synonyms = {
        "iit delhi": ["indian institute of technology, delhi", "indian institute of technology delhi", "iitd", "iit delhi"],
        "cuj": ["central university of jharkhand", "cuj"],
        "bhu": ["banaras hindu university", "bhu"],
        "jnu": ["jawaharlal nehru university", "jnu"],
        "du": ["university of delhi", "delhi university", "du"],
    }
    for syn_key, aliases in synonyms.items():
        if any(alias in o for alias in aliases) and any(alias in a for alias in aliases):
            return True
            
    return False

@router.get("/stats")
def get_institution_stats(
    current_officer: User = Depends(get_current_institution_officer),
    db: Session = Depends(get_db)
):
    officer_inst = (current_officer.institution_name or current_officer.institution or "").strip()
    apps = db.query(Application).join(User, Application.user_id == User.id).all()
    
    matched = []
    for app in apps:
        app_inst = (
            (app.form_data or {}).get("institution") or 
            (app.form_data or {}).get("institute_name") or 
            app.applicant.institution or 
            app.applicant.institution_name or ""
        )
        if current_officer.role == "admin" or _matches_institution(officer_inst, app_inst):
            matched.append(app)
            
    total = len(matched)
    verified = sum(1 for a in matched if a.enrollment_verified)
    pending = sum(1 for a in matched if not a.enrollment_verified and a.status not in ["Needs Review", "Rejected"])
    rejected = sum(1 for a in matched if not a.enrollment_verified and a.status in ["Needs Review", "Rejected"])

    return {
        "institution_name": officer_inst or "All Institutions (Admin Mode)",
        "officer_name": current_officer.full_name,
        "total_applications": total,
        "verified_count": verified,
        "pending_count": pending,
        "rejected_count": rejected
    }

@router.get("/applications", response_model=List[ApplicationOut])
def get_institution_applications(
    current_officer: User = Depends(get_current_institution_officer),
    db: Session = Depends(get_db)
):
    officer_inst = (current_officer.institution_name or current_officer.institution or "").strip()
    apps = db.query(Application).join(User, Application.user_id == User.id).order_by(Application.created_at.desc()).all()
    
    matched = []
    for app in apps:
        app_inst = (
            (app.form_data or {}).get("institution") or 
            (app.form_data or {}).get("institute_name") or 
            app.applicant.institution or 
            app.applicant.institution_name or ""
        )
        if current_officer.role == "admin" or _matches_institution(officer_inst, app_inst):
            matched.append(app)
            
    return matched

@router.get("/applications/{app_id}", response_model=ApplicationDetailOut)
def get_institution_application_detail(
    app_id: int,
    current_officer: User = Depends(get_current_institution_officer),
    db: Session = Depends(get_db)
):
    app = db.query(Application).filter(Application.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
        
    officer_inst = (current_officer.institution_name or current_officer.institution or "").strip()
    app_inst = (
        (app.form_data or {}).get("institution") or 
        (app.form_data or {}).get("institute_name") or 
        app.applicant.institution or 
        app.applicant.institution_name or ""
    )
    if current_officer.role != "admin" and not _matches_institution(officer_inst, app_inst):
        raise HTTPException(status_code=403, detail="Unauthorized: Application does not belong to your institution")

    return app

@router.post("/applications/{app_id}/verify-enrollment")
def verify_institution_enrollment(
    app_id: int,
    payload: EnrollmentVerificationRequest,
    current_officer: User = Depends(get_current_institution_officer),
    db: Session = Depends(get_db)
):
    app = db.query(Application).filter(Application.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    officer_inst = (current_officer.institution_name or current_officer.institution or "Institution").strip()
    app_inst = (
        (app.form_data or {}).get("institution") or 
        (app.form_data or {}).get("institute_name") or 
        app.applicant.institution or 
        app.applicant.institution_name or ""
    )
    if current_officer.role != "admin" and not _matches_institution(officer_inst, app_inst):
        raise HTTPException(status_code=403, detail="Unauthorized: Student is not registered under your institution")

    enrollment_no = payload.enrollment_number or (app.form_data or {}).get("enrollment_number") or (app.form_data or {}).get("roll_number") or "N/A"

    verif = EnrollmentVerification(
        application_id=app.id,
        verified_by_user_id=current_officer.id,
        institution_name=officer_inst,
        enrollment_number=enrollment_no,
        enrolled=payload.enrolled,
        remarks=payload.remarks,
        verified_at=datetime.utcnow()
    )
    db.add(verif)
    db.flush()

    old_status = app.status
    app.enrollment_verified = payload.enrolled
    app.enrollment_verification_id = verif.id

    if not payload.enrolled:
        app.status = "Needs Review"
        defic = Deficiency(
            application_id=app.id,
            doc_type="enrollment_verification",
            reason=f"Institution reported: student not enrolled ({payload.remarks or 'Discontinued/Unverified'})",
            status="Open",
            created_at=datetime.utcnow()
        )
        db.add(defic)
        
        # Email notification to student
        notification_service.send_email(
            to_email=app.applicant.email,
            subject=f"Urgent: MoTA Application {app.application_number} - Institution Verification Issue",
            body_html=f"""
            <p>Dear {app.applicant.full_name},</p>
            <p>Your Institution Nodal Officer at <strong>{officer_inst}</strong> was unable to confirm your active student enrollment for application <strong>{app.application_number}</strong>.</p>
            <p><strong>Officer Remarks:</strong> {payload.remarks or 'Student enrollment not found in institutional register.'}</p>
            <p>Please contact your university nodal authority immediately to resolve this discrepancy.</p>
            """,
            application_id=app.id
        )
    else:
        if app.status == "Submitted":
            app.status = "Under Verification"
            
        notification_service.send_email(
            to_email=app.applicant.email,
            subject=f"MoTA Application {app.application_number} - Institution Enrollment Verified",
            body_html=f"""
            <p>Dear {app.applicant.full_name},</p>
            <p>Your enrollment has been successfully <strong>VERIFIED</strong> by the Institution Nodal Officer at <strong>{officer_inst}</strong>.</p>
            <p>Your application is now advancing to Ministry Scrutiny.</p>
            """,
            application_id=app.id
        )

    # Activity Log
    act_log = ActivityLog(
        application_id=app.id,
        action="Institution Enrollment Verified" if payload.enrolled else "Institution Enrollment Flagged/Rejected",
        actor=f"{current_officer.full_name} ({officer_inst})",
        stage=app.status,
        remarks=f"Enrollment No: {enrollment_no}. Enrolled: {payload.enrolled}. Remarks: {payload.remarks or 'Verified'}",
        created_at=datetime.utcnow()
    )
    db.add(act_log)

    # Cryptographic Audit Ledger Entry (Priority 5)
    log_action(
        db=db,
        application_id=app.id,
        actor_name=current_officer.full_name,
        actor_role="Institution Nodal Officer",
        action="Institution Enrollment Verification",
        previous_state=old_status,
        new_state=app.status,
        remarks=f"Institution: {officer_inst}. Status: {'Enrolled' if payload.enrolled else 'Not Enrolled'}. Remarks: {payload.remarks}",
        stage="Institution Verification",
        user_id=current_officer.id
    )

    db.commit()
    db.refresh(app)

    return {
        "message": "Institution verification recorded successfully",
        "enrollment_verified": app.enrollment_verified,
        "application_status": app.status,
        "verification_id": verif.id
    }
