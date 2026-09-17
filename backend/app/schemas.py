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
    institution_name: Optional[str] = None
    course: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp: str
    new_password: str

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
    institution_name: Optional[str] = None
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

class SchemeUpdateRequest(BaseModel):
    income_ceiling: Optional[float] = None
    min_marks: Optional[float] = None
    financial_assistance: Optional[str] = None
    objective: Optional[str] = None
    is_active: Optional[bool] = None

class DocumentOut(BaseModel):
    id: int
    application_id: int
    doc_type: str
    file_name: str
    file_size: int
    status: str
    confidence_score: float
    file_hash: Optional[str] = None
    predicted_type: Optional[str] = None
    classifier_confidence: Optional[float] = None
    type_mismatch: bool = False
    tampering_signals: Dict[str, Any] = {}
    is_digilocker_issued: bool = False
    digilocker_uri: Optional[str] = None
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
    risk_level: str = "LOW"
    risk_score: float = 0.0
    is_digilocker_verified: bool = False
    is_aadhaar_verified: bool = False
    submission_date: datetime
    applicant: Optional[UserOut] = None
    scheme: Optional[SchemeOut] = None
    parent_application_id: Optional[int] = None
    enrollment_verified: bool = False
    enrollment_verification_id: Optional[int] = None

    class Config:
        from_attributes = True

class ApplicationDetailOut(ApplicationOut):
    documents: List[DocumentOut] = []
    deficiencies: List[DeficiencyOut] = []
    timeline_logs: List[ActivityLogOut] = []
    risk_assessment: Dict[str, Any] = {}
    aadhaar_data: Dict[str, Any] = {}
    disbursement_status: Optional[str] = None
    disbursement_amount: Optional[float] = None
    renewal_due_date: Optional[str] = None
    parent_application_id: Optional[int] = None

class RenewalSubmitRequest(BaseModel):
    progress_report: str
    continuation_institution: str
    continuation_course: str
    bank_account_confirmed: bool
    current_year_semester: Optional[str] = None
    supervisor_guide_name: Optional[str] = None
    marks_or_grade: Optional[str] = None


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

class NotificationLogOut(BaseModel):
    id: int
    recipient_email: Optional[str] = None
    recipient_phone: Optional[str] = None
    notification_type: str
    subject: str
    body_preview: Optional[str] = None
    status: str
    application_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True

class EnrollmentVerificationRequest(BaseModel):
    enrolled: bool
    enrollment_number: Optional[str] = None
    remarks: Optional[str] = None

class EnrollmentVerificationOut(BaseModel):
    id: int
    application_id: int
    verified_by_user_id: int
    institution_name: str
    enrollment_number: Optional[str] = None
    enrolled: bool
    remarks: Optional[str] = None
    verified_at: datetime

    class Config:
        from_attributes = True

