from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="applicant")  # "applicant" or "admin"
    full_name = Column(String(255), nullable=False)
    st_cert_number = Column(String(100), nullable=True)
    phone = Column(String(50), nullable=True)
    state = Column(String(100), nullable=True)
    community_tribe = Column(String(100), nullable=True)
    institution = Column(String(255), nullable=True)
    institution_name = Column(String(255), nullable=True)
    course = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    applications = relationship("Application", back_populates="applicant", cascade="all, delete-orphan")

class Scheme(Base):
    __tablename__ = "schemes"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)  # "NFST", "NOS"
    name = Column(String(255), nullable=False)
    full_title = Column(String(500), nullable=False)
    objective = Column(Text, nullable=True)
    financial_assistance = Column(Text, nullable=True)
    target_group = Column(String(255), default="Scheduled Tribe (ST) Students")
    income_ceiling = Column(Float, default=600000.0)
    min_marks = Column(Float, default=55.0)
    is_active = Column(Boolean, default=True)

    # Core configurability JSON columns:
    required_documents = Column(JSON, default=list)
    eligibility_rules = Column(JSON, default=dict)
    form_fields = Column(JSON, default=list)
    merit_weights = Column(JSON, default=dict)

    applications = relationship("Application", back_populates="scheme")

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    application_number = Column(String(100), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    scheme_id = Column(Integer, ForeignKey("schemes.id"), nullable=False)
    status = Column(String(50), default="Submitted")
    # Statuses: "Submitted", "Under Verification", "Needs Review", "Scrutiny", "Selected", "Rejected", "Post-Selection"

    form_data = Column(JSON, default=dict)
    eligibility_passed = Column(Boolean, default=True)
    eligibility_notes = Column(JSON, default=list)
    calculated_merit_score = Column(Float, default=0.0)
    merit_rank = Column(Integer, nullable=True)

    disbursement_status = Column(String(100), default="Pending Approval")
    disbursement_amount = Column(Float, default=0.0)
    renewal_due_date = Column(String(50), nullable=True)
    parent_application_id = Column(Integer, ForeignKey("applications.id"), nullable=True)
    enrollment_verified = Column(Boolean, default=False)
    enrollment_verification_id = Column(Integer, ForeignKey("enrollment_verifications.id"), nullable=True)

    # Risk & Fraud Assessment
    risk_assessment = Column(JSON, default=dict)
    risk_level = Column(String(20), default="LOW", index=True)  # "LOW", "MEDIUM", "HIGH"
    risk_score = Column(Float, default=0.0)

    # e-Governance & Integrations
    is_digilocker_verified = Column(Boolean, default=False)
    is_aadhaar_verified = Column(Boolean, default=False)
    aadhaar_data = Column(JSON, default=dict)

    submission_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    applicant = relationship("User", back_populates="applications")
    scheme = relationship("Scheme", back_populates="applications")
    documents = relationship("Document", back_populates="application", cascade="all, delete-orphan")
    deficiencies = relationship("Deficiency", back_populates="application", cascade="all, delete-orphan")
    timeline_logs = relationship("ActivityLog", back_populates="application", cascade="all, delete-orphan")
    audit_ledger = relationship("AuditLogEntry", back_populates="application", cascade="all, delete-orphan", order_by="AuditLogEntry.id")
    enrollment_verification = relationship("EnrollmentVerification", foreign_keys=[enrollment_verification_id])

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)
    doc_type = Column(String(100), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, default=0)
    file_hash = Column(String(64), nullable=True, index=True)  # SHA-256 for duplicate file detection
    status = Column(String(50), default="Pending")
    # "Pending", "Verified", "Needs Review", "Missing/Unreadable"

    confidence_score = Column(Float, default=0.0)
    extracted_data = Column(JSON, default=dict)
    comparison_data = Column(JSON, default=dict)
    ocr_text = Column(Text, nullable=True)

    # Document Classifier output
    predicted_type = Column(String(100), nullable=True)
    classifier_confidence = Column(Float, nullable=True)
    type_mismatch = Column(Boolean, default=False)

    # Forensic & Tampering signals
    tampering_signals = Column(JSON, default=dict)

    # DigiLocker issuer flag
    is_digilocker_issued = Column(Boolean, default=False)
    digilocker_uri = Column(String(255), nullable=True)

    upload_date = Column(DateTime, default=datetime.utcnow)

    application = relationship("Application", back_populates="documents")

class Deficiency(Base):
    __tablename__ = "deficiencies"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    doc_type = Column(String(100), nullable=True)
    flagged_by = Column(String(100), default="MoTA Scrutiny Officer")
    reason = Column(Text, nullable=False)
    status = Column(String(50), default="Open")  # "Open", "Resolved"
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

    application = relationship("Application", back_populates="deficiencies")

class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)
    action = Column(String(100), nullable=False)
    actor = Column(String(100), default="System")
    stage = Column(String(50), nullable=False)
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    application = relationship("Application", back_populates="timeline_logs")

class AuditLogEntry(Base):
    __tablename__ = "audit_log_entries"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    actor_name = Column(String(255), nullable=False)
    actor_role = Column(String(50), nullable=False)
    action = Column(String(100), nullable=False)
    previous_state = Column(String(50), nullable=True)
    new_state = Column(String(50), nullable=True)
    stage = Column(String(50), nullable=False)
    remarks = Column(Text, nullable=True)
    document_id = Column(Integer, nullable=True)
    details = Column(JSON, default=dict)
    previous_hash = Column(String(64), nullable=False)
    entry_hash = Column(String(64), nullable=False, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    application = relationship("Application", back_populates="audit_ledger")

class NotificationLog(Base):
    __tablename__ = "notification_logs"

    id = Column(Integer, primary_key=True, index=True)
    recipient_email = Column(String(255), nullable=True)
    recipient_phone = Column(String(50), nullable=True)
    notification_type = Column(String(50), nullable=False)
    subject = Column(String(255), nullable=False)
    body_preview = Column(String(255), nullable=True)
    status = Column(String(20), default="SENT")  # "SENT", "SIMULATED", "FAILED"
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String(10), nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
 
class EnrollmentVerification(Base):
    __tablename__ = "enrollment_verifications"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)
    verified_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    institution_name = Column(String(255), nullable=False)
    enrollment_number = Column(String(100), nullable=True)
    enrolled = Column(Boolean, default=True)
    remarks = Column(Text, nullable=True)
    verified_at = Column(DateTime, default=datetime.utcnow)

    application = relationship("Application", foreign_keys=[application_id])
    verified_by = relationship("User", foreign_keys=[verified_by_user_id])

