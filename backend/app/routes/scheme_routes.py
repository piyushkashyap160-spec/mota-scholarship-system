from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Scheme, User
from ..schemas import SchemeOut, SchemeUpdateRequest
from ..auth import get_current_admin
from ..audit import log_action

router = APIRouter(prefix="/api/schemes", tags=["Schemes"])

@router.get("", response_model=List[SchemeOut])
def get_schemes(db: Session = Depends(get_db)):
    schemes = db.query(Scheme).filter(Scheme.is_active == True).all()
    return schemes

@router.get("/{code_or_id}", response_model=SchemeOut)
def get_scheme(code_or_id: str, db: Session = Depends(get_db)):
    if code_or_id.isdigit():
        scheme = db.query(Scheme).filter(Scheme.id == int(code_or_id)).first()
    else:
        scheme = db.query(Scheme).filter(Scheme.code == code_or_id.upper()).first()

    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")
    return scheme

@router.put("/{code_or_id}", response_model=SchemeOut)
def update_scheme_rules(
    code_or_id: str,
    payload: SchemeUpdateRequest,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Update scheme eligibility rules and thresholds (admin only).
    NOTE: Editing required_documents, form_fields, or merit_weights is intentionally
    disallowed via this endpoint as those are structural schema definitions requiring
    database migrations and form template validation. Only operational eligibility threshold
    parameters (income ceiling, qualifying percentage, financial assistance, objective, active status)
    are dynamically editable.
    """
    if code_or_id.isdigit():
        scheme = db.query(Scheme).filter(Scheme.id == int(code_or_id)).first()
    else:
        scheme = db.query(Scheme).filter(Scheme.code == code_or_id.upper()).first()

    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")

    prev_state = f"Income: {scheme.income_ceiling}, Marks: {scheme.min_marks}%, Active: {scheme.is_active}"

    # Update fields if provided in payload
    if payload.income_ceiling is not None:
        scheme.income_ceiling = payload.income_ceiling
        rules = dict(scheme.eligibility_rules or {})
        rules["income_ceiling"] = payload.income_ceiling
        scheme.eligibility_rules = rules

    if payload.min_marks is not None:
        scheme.min_marks = payload.min_marks
        rules = dict(scheme.eligibility_rules or {})
        rules["min_qualifying_percentage"] = payload.min_marks
        scheme.eligibility_rules = rules

    if payload.financial_assistance is not None:
        scheme.financial_assistance = payload.financial_assistance

    if payload.objective is not None:
        scheme.objective = payload.objective

    if payload.is_active is not None:
        scheme.is_active = payload.is_active

    new_state = f"Income: {scheme.income_ceiling}, Marks: {scheme.min_marks}%, Active: {scheme.is_active}"

    # Log to audit trail (Priority 5)
    log_action(
        db=db,
        actor_name=current_admin.full_name,
        actor_role="Admin",
        action="Scheme Rule Updated",
        previous_state=prev_state,
        new_state=new_state,
        remarks=f"Scheme rules for {scheme.code} updated by administrator.",
        stage="Scheme Administration",
        user_id=current_admin.id
    )

    db.commit()
    db.refresh(scheme)
    return scheme

