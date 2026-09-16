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

    submission_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    applicant = relationship("User", back_populates="applications")
    scheme = relationship("Scheme", back_populates="applications")
    documents = relationship("Document", back_populates="application", cascade="all, delete-orphan")
    deficiencies = relationship("Deficiency", back_populates="application", cascade="all, delete-orphan")
    timeline_logs = relationship("ActivityLog", back_populates="application", cascade="all, delete-orphan")

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)
    doc_type = Column(String(100), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, default=0)
    status = Column(String(50), default="Pending")
    # "Pending", "Verified", "Needs Review", "Missing/Unreadable"

    confidence_score = Column(Float, default=0.0)
    extracted_data = Column(JSON, default=dict)
    comparison_data = Column(JSON, default=dict)
    ocr_text = Column(Text, nullable=True)
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
