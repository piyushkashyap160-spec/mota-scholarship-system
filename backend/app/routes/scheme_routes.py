from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Scheme
from ..schemas import SchemeOut

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
