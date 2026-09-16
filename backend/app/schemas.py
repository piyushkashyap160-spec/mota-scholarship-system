from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    user_id: int
    full_name: str
    email: str

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None
    user_id: Optional[int] = None

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: str = "applicant"
    st_cert_number: Optional[str] = None
    phone: Optional[str] = None
    state: Optional[str] = None
    community_tribe: Optional[str] = None
    institution: Optional[str] = None
    course: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: str
    role: str
    full_name: str
    st_cert_number: Optional[str] = None
    phone: Optional[str] = None
    state: Optional[str] = None
    community_tribe: Optional[str] = None
    institution: Optional[str] = None
    course: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class SchemeOut(BaseModel):
    id: int
    code: str
    name: str
    full_title: str
    objective: Optional[str] = None
    financial_assistance: Optional[str] = None
    target_group: str
    income_ceiling: float
    min_marks: float
    is_active: bool
    required_documents: List[Dict[str, Any]]
    eligibility_rules: Dict[str, Any]
    form_fields: List[Dict[str, Any]]
    merit_weights: Dict[str, Any]

    class Config:
        from_attributes = True

class DocumentOut(BaseModel):
    id: int
    application_id: int
    doc_type: str
    file_name: str
    file_size: int
    status: str
    confidence_score: float
    extracted_data: Dict[str, Any]
    comparison_data: Dict[str, Any]
    upload_date: datetime

    class Config:
        from_attributes = True

class DeficiencyOut(BaseModel):
    id: int
    application_id: int
    document_id: Optional[int] = None
    doc_type: Optional[str] = None
    flagged_by: str
    reason: str
    status: str
    created_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ActivityLogOut(BaseModel):
    id: int
    action: str
    actor: str
    stage: str
    remarks: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ApplicationOut(BaseModel):
    id: int
    application_number: str
    user_id: int
    scheme_id: int
    status: str
    form_data: Dict[str, Any]
    eligibility_passed: bool
    eligibility_notes: List[str]
    calculated_merit_score: float
    merit_rank: Optional[int] = None
    submission_date: datetime
    applicant: Optional[UserOut] = None
    scheme: Optional[SchemeOut] = None

    class Config:
        from_attributes = True

class ApplicationDetailOut(ApplicationOut):
    documents: List[DocumentOut] = []
    deficiencies: List[DeficiencyOut] = []
    timeline_logs: List[ActivityLogOut] = []
    disbursement_status: Optional[str] = None
    disbursement_amount: Optional[float] = None
    renewal_due_date: Optional[str] = None

class ApplicationSubmit(BaseModel):
    scheme_id: int
    form_data: Dict[str, Any]
    documents: List[Dict[str, Any]]

class AdminActionRequest(BaseModel):
    action: str  # "approve", "reject", "request_resubmission", "mark_verified"
    stage: Optional[str] = "Scrutiny"
    remarks: str
    document_id: Optional[int] = None
    doc_type: Optional[str] = None

class MeritWeightConfig(BaseModel):
    marks_weight: float = 0.70
    income_weight: float = 0.30

class ResubmitDocumentRequest(BaseModel):
    deficiency_id: int
    file_name: str
    file_data: Optional[str] = None
