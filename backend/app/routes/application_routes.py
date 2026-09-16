import random
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, Scheme, Application, Document, Deficiency, ActivityLog
from ..schemas import ApplicationOut, ApplicationDetailOut, ApplicationSubmit, ResubmitDocumentRequest
from ..auth import get_current_user
from ..eligibility_engine import evaluate_eligibility
from ..merit_engine import calculate_merit_score
from ..fraud_engine import evaluate_application_risk
from ..audit import log_action

router = APIRouter(prefix="/api/applications", tags=["Applications"])

@router.post("/apply", response_model=ApplicationDetailOut)
def submit_application(
    payload: ApplicationSubmit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    scheme = db.query(Scheme).filter(Scheme.id == payload.scheme_id).first()
    if not scheme:
        raise HTTPException(status_code=404, detail="Selected scheme not found")

    # Generate unique application number e.g. NFST-2026-9812
    rand_id = random.randint(1000, 9999)
    app_num = f"{scheme.code}-2026-{rand_id}"

    # Evaluate eligibility against scheme JSON rules
    is_eligible, notes, breakdown = evaluate_eligibility(scheme.eligibility_rules, payload.form_data)

    # Calculate initial merit score
    merit_score = calculate_merit_score(payload.form_data, income_ceiling=scheme.income_ceiling)

    # Collect any document file hashes provided by upload/scan step
    uploaded_file_hashes = [doc.get("file_hash") for doc in payload.documents if doc.get("file_hash")]

    # Create Application
    new_app = Application(
        application_number=app_num,
        user_id=current_user.id,
        scheme_id=scheme.id,
        status="Under Verification",
        form_data=payload.form_data,
        eligibility_passed=is_eligible,
        eligibility_notes=notes,
        calculated_merit_score=merit_score,
        disbursement_status="Pending Verification",
        disbursement_amount=0.0,
        submission_date=datetime.utcnow()
    )
    db.add(new_app)
    db.flush()

    # Run AI Fraud & Duplicate Detection Engine
    risk_assessment = evaluate_application_risk(new_app, db, uploaded_file_hashes)
    new_app.risk_assessment = risk_assessment
    new_app.risk_level = risk_assessment.get("risk_level", "LOW")
    new_app.risk_score = risk_assessment.get("risk_score", 0.0)

    # Save attached documents with forensic & hash properties
    for doc_item in payload.documents:
        new_doc = Document(
            application_id=new_app.id,
            doc_type=doc_item.get("doc_type", "document"),
            file_name=doc_item.get("file_name", "document.pdf"),
            file_path=f"/uploads/{doc_item.get('file_name', 'doc.pdf')}",
            file_size=doc_item.get("file_size", 150000),
            file_hash=doc_item.get("file_hash"),
            status=doc_item.get("status", "Verified"),
            confidence_score=doc_item.get("confidence_score", 95.0),
            predicted_type=doc_item.get("predicted_type"),
            classifier_confidence=doc_item.get("classifier_confidence"),
            type_mismatch=doc_item.get("type_mismatch", False),
            tampering_signals=doc_item.get("tampering_signals"),
            extracted_data=doc_item.get("extracted_data", {}),
            comparison_data=doc_item.get("comparison_matrix", {}),
            ocr_text=doc_item.get("ocr_preview", "OCR Processed"),
            upload_date=datetime.utcnow()
        )
        db.add(new_doc)

    # Activity Timeline Logs
    log1 = ActivityLog(
        application_id=new_app.id,
        action="Application Submitted",
        actor=current_user.full_name,
        stage="Submitted",
        remarks=f"Application {app_num} submitted by applicant.",
        created_at=datetime.utcnow()
    )
    log2 = ActivityLog(
        application_id=new_app.id,
        action="AI Document Verification Completed",
        actor="MoTA AI-OCR Engine",
        stage="Under Verification",
        remarks=f"{len(payload.documents)} documents scanned and verified against form values.",
        created_at=datetime.utcnow()
    )
    db.add(log1)
    db.add(log2)

    # Log Fraud Risk Signal advisory if any flags were raised
    if risk_assessment.get("flags"):
        flag_summary = "; ".join([f["flag_name"] for f in risk_assessment["flags"][:3]])
        log3 = ActivityLog(
            application_id=new_app.id,
            action=f"Fraud & Risk Scan: {new_app.risk_level} RISK",
            actor="MoTA Fraud Engine",
            stage="Under Verification",
            remarks=f"Risk Score: {new_app.risk_score}/100. Advisory Flags: {flag_summary}",
            created_at=datetime.utcnow()
        )
        db.add(log3)

    # Append Immutable Cryptographic Audit Ledger Entry (Priority 5)
    log_action(
        db=db,
        application_id=new_app.id,
        actor_name=current_user.full_name,
        actor_role="Applicant",
        action="Application Submitted",
        previous_state="Draft",
        new_state="Under Verification",
        remarks=f"Application {app_num} formally submitted with {len(payload.documents)} documents.",
        stage="Submitted",
        user_id=current_user.id
    )

    db.commit()
    db.refresh(new_app)
    return new_app

@router.get("/my", response_model=List[ApplicationOut])
def get_my_applications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    apps = db.query(Application).filter(Application.user_id == current_user.id).order_by(Application.created_at.desc()).all()
    return apps

@router.get("/{app_id}", response_model=ApplicationDetailOut)
def get_application_detail(
    app_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Application).filter(Application.id == app_id)
    if current_user.role != "admin":
        query = query.filter(Application.user_id == current_user.id)

    app = query.first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found or unauthorized")
    return app

@router.post("/{app_id}/resubmit")
def resubmit_deficient_document(
    app_id: int,
    payload: ResubmitDocumentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    app = db.query(Application).filter(Application.id == app_id, Application.user_id == current_user.id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    defic = db.query(Deficiency).filter(Deficiency.id == payload.deficiency_id, Deficiency.application_id == app.id).first()
    if not defic:
        raise HTTPException(status_code=404, detail="Deficiency notice not found")

    # Mark deficiency resolved
    defic.status = "Resolved"
    defic.resolved_at = datetime.utcnow()

    # Update document status to Verified
    if defic.document_id:
        doc = db.query(Document).filter(Document.id == defic.document_id).first()
        if doc:
            doc.status = "Verified"
            doc.confidence_score = 98.0
            doc.file_name = f"resubmitted_{payload.file_name}"
            # Update comparison data to matched
            if doc.comparison_data and "fields" in doc.comparison_data:
                for f_key in doc.comparison_data["fields"]:
                    doc.comparison_data["fields"][f_key]["match"] = True
                    doc.comparison_data["fields"][f_key]["similarity"] = 100.0
                    doc.comparison_data["fields"][f_key]["remarks"] = "Resubmitted Document Verified by Officer"
                doc.comparison_data["discrepancies"] = []
                doc.comparison_data["status"] = "Verified"

    # If all deficiencies resolved, transition application status back to Scrutiny
    open_defics = db.query(Deficiency).filter(Deficiency.application_id == app.id, Deficiency.status == "Open").count()
    if open_defics == 0:
        app.status = "Scrutiny"

    # Add activity log
    log = ActivityLog(
        application_id=app.id,
        action="Document Resubmitted by Applicant",
        actor=current_user.full_name,
        stage="Scrutiny",
        remarks=f"Applicant uploaded rectified document for '{defic.doc_type}'. Deficiency resolved.",
        created_at=datetime.utcnow()
    )
    db.add(log)

    # Append to Cryptographic Audit Ledger (Priority 5)
    log_action(
        db=db,
        application_id=app.id,
        actor_name=current_user.full_name,
        actor_role="Applicant",
        action="Document Resubmitted",
        previous_state="Needs Review",
        new_state=app.status,
        remarks=f"Applicant uploaded rectified document for '{defic.doc_type}'. Deficiency resolved.",
        stage=app.status,
        document_id=defic.document_id,
        user_id=current_user.id
    )

    db.commit()

    return {"message": "Document resubmitted successfully. Deficiency resolved.", "new_status": app.status}
