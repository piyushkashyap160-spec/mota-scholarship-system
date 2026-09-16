from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db
from ..models import User, Scheme, Application, Document, Deficiency, ActivityLog
from ..schemas import ApplicationOut, ApplicationDetailOut, AdminActionRequest, MeritWeightConfig
from ..auth import get_current_admin
from ..merit_engine import rank_applications

router = APIRouter(prefix="/api/admin", tags=["Admin Portal & Scrutiny"])

@router.get("/applications", response_model=List[ApplicationOut])
def list_applications(
    scheme: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    query = db.query(Application).join(User, Application.user_id == User.id).join(Scheme, Application.scheme_id == Scheme.id)

    if scheme and scheme.upper() != "ALL":
        query = query.filter(Scheme.code == scheme.upper())

    if status and status != "All":
        query = query.filter(Application.status == status)

    if state and state != "All":
        query = query.filter(User.state == state)

    if search:
        s = f"%{search}%"
        query = query.filter(
            (Application.application_number.ilike(s)) |
            (User.full_name.ilike(s)) |
            (User.st_cert_number.ilike(s)) |
            (User.email.ilike(s))
        )

    apps = query.order_by(Application.created_at.desc()).all()
    return apps

@router.get("/applications/{app_id}", response_model=ApplicationDetailOut)
def get_admin_application_detail(
    app_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    app = db.query(Application).filter(Application.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return app

@router.post("/applications/{app_id}/action")
def take_application_action(
    app_id: int,
    action_in: AdminActionRequest,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    app = db.query(Application).filter(Application.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    act = action_in.action.lower()
    if act == "approve":
        app.status = "Selected"
        app.disbursement_status = "Active Fellowship Disbursement"
        app.disbursement_amount = 432000.0 if app.scheme.code == "NFST" else 1850000.0
        app.renewal_due_date = "2027-03-31"

        log = ActivityLog(
            application_id=app.id,
            action="Application Approved & Selected",
            actor=current_admin.full_name,
            stage="Selected",
            remarks=action_in.remarks or "Candidate selected by Scrutiny Committee for award of Fellowship/Scholarship.",
            created_at=datetime.utcnow()
        )
        db.add(log)

    elif act == "reject":
        app.status = "Rejected"
        app.disbursement_status = "Ineligible"
        log = ActivityLog(
            application_id=app.id,
            action="Application Rejected",
            actor=current_admin.full_name,
            stage="Rejected",
            remarks=action_in.remarks or "Application does not fulfill the mandatory eligibility criteria.",
            created_at=datetime.utcnow()
        )
        db.add(log)

    elif act == "request_resubmission":
        app.status = "Needs Review"
        app.disbursement_status = "Action Required by Candidate"

        # Create deficiency record
        defic = Deficiency(
            application_id=app.id,
            document_id=action_in.document_id,
            doc_type=action_in.doc_type,
            flagged_by=current_admin.full_name,
            reason=action_in.remarks,
            status="Open",
            created_at=datetime.utcnow()
        )
        db.add(defic)

        # Update document status if provided
        if action_in.document_id:
            doc = db.query(Document).filter(Document.id == action_in.document_id).first()
            if doc:
                doc.status = "Needs Review"

        log = ActivityLog(
            application_id=app.id,
            action="Deficiency Raised by Scrutiny Officer",
            actor=current_admin.full_name,
            stage="Needs Review",
            remarks=action_in.remarks,
            created_at=datetime.utcnow()
        )
        db.add(log)

    else:
        raise HTTPException(status_code=400, detail=f"Unsupported action '{action_in.action}'")

    db.commit()
    db.refresh(app)
    return {"message": f"Action '{action_in.action}' recorded successfully", "current_status": app.status}

@router.post("/merit-ranking")
def get_merit_ranking(
    weights: MeritWeightConfig,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    apps = db.query(Application).filter(Application.eligibility_passed == True).all()
    ranked_list = rank_applications(apps, marks_weight=weights.marks_weight, income_weight=weights.income_weight)
    return {
        "weights_applied": {"marks_weight": weights.marks_weight, "income_weight": weights.income_weight},
        "total_eligible_candidates": len(ranked_list),
        "rankings": ranked_list
    }

@router.get("/analytics")
def get_analytics(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    total_apps = db.query(Application).count()
    selected_apps = db.query(Application).filter(Application.status == "Selected").count()
    review_apps = db.query(Application).filter(Application.status == "Needs Review").count()
    rejected_apps = db.query(Application).filter(Application.status == "Rejected").count()
    scrutiny_apps = db.query(Application).filter(Application.status.in_(["Scrutiny", "Under Verification"])).count()
    submitted_apps = db.query(Application).filter(Application.status == "Submitted").count()

    total_funds = db.query(func.sum(Application.disbursement_amount)).scalar() or 0.0

    # Scheme distribution
    nfst_count = db.query(Application).join(Scheme).filter(Scheme.code == "NFST").count()
    nos_count = db.query(Application).join(Scheme).filter(Scheme.code == "NOS").count()

    # State distribution
    state_rows = db.query(User.state, func.count(Application.id))\
        .join(Application, User.id == Application.user_id)\
        .group_by(User.state).all()
    state_data = [{"state": r[0] or "Other", "count": r[1]} for r in state_rows]
    state_data.sort(key=lambda x: x["count"], reverse=True)

    # Frequently flagged documents
    flagged_docs_rows = db.query(Deficiency.doc_type, func.count(Deficiency.id))\
        .group_by(Deficiency.doc_type).all()
    flagged_docs = [{"doc_type": r[0] or "general", "count": r[1]} for r in flagged_docs_rows]

    return {
        "kpis": {
            "total_applications": total_apps,
            "selected_scholars": selected_apps,
            "needs_review_count": review_apps,
            "rejected_count": rejected_apps,
            "in_scrutiny": scrutiny_apps,
            "submitted_count": submitted_apps,
            "auto_pass_rate": round((total_apps - review_apps) / max(total_apps, 1) * 100, 1),
            "total_disbursed_funds_inr": total_funds
        },
        "status_distribution": [
            {"status": "Selected", "count": selected_apps, "color": "#10B981"},
            {"status": "Under Scrutiny", "count": scrutiny_apps, "color": "#3B82F6"},
            {"status": "Needs Review", "count": review_apps, "color": "#F59E0B"},
            {"status": "Submitted", "count": submitted_apps, "color": "#6B7280"},
            {"status": "Rejected", "count": rejected_apps, "color": "#EF4444"}
        ],
        "scheme_distribution": [
            {"scheme": "NFST (National Fellowship)", "code": "NFST", "count": nfst_count},
            {"scheme": "NOS (Overseas Scholarship)", "code": "NOS", "count": nos_count}
        ],
        "state_distribution": state_data,
        "frequently_flagged_documents": flagged_docs,
        "processing_velocity": [
            {"stage": "Submission to OCR Scan", "average_time": "Instant (3.2 seconds)"},
            {"stage": "AI Cross-Check to Scrutiny", "average_time": "4.5 hours"},
            {"stage": "Committee Final Decision", "average_time": "3.8 days"},
            {"stage": "Direct Benefit Transfer (DBT)", "average_time": "24 hours"}
        ]
    }
