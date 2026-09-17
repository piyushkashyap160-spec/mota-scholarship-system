import re
from difflib import SequenceMatcher
from typing import Dict, Any, List, Tuple
from sqlalchemy.orm import Session

def string_similarity(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, str(a).strip().lower(), str(b).strip().lower()).ratio()

def evaluate_application_risk(
    application: Any,
    db: Session,
    uploaded_file_hashes: List[str] = None
) -> Dict[str, Any]:
    """
    Evaluates fraud and duplicate signals across:
    1. ST Certificate Number collisions
    2. Fuzzy Name + DOB identity collisions across different accounts
    3. Bank Account Number collisions (DBT diversion signals)
    4. Exact Document SHA-256 hash collisions
    5. Dual simultaneous scheme applications (NFST + NOS)
    """
    from .models import Application, User, Scheme, Document

    flags = []
    risk_score = 0.0

    current_app_id = application.id if hasattr(application, 'id') else None
    user_id = application.user_id if hasattr(application, 'user_id') else None
    form_data = getattr(application, 'form_data', {}) or {}
    scheme_id = getattr(application, 'scheme_id', None)

    current_st_cert = str(form_data.get("st_cert_number", "")).strip().upper()
    current_name = str(form_data.get("full_name", "")).strip()
    current_dob = str(form_data.get("dob", "")).strip()
    current_bank = str(form_data.get("bank_account_no", "")).strip()

    # Query other applications (excluding the current one)
    other_apps_query = db.query(Application).join(User, Application.user_id == User.id).join(Scheme, Application.scheme_id == Scheme.id)
    if current_app_id:
        other_apps_query = other_apps_query.filter(Application.id != current_app_id)
    
    other_apps = other_apps_query.all()

    # 1. Check ST Certificate collision
    if current_st_cert and len(current_st_cert) >= 4:
        for other in other_apps:
            other_fd = other.form_data or {}
            other_st = str(other_fd.get("st_cert_number", "")).strip().upper()
            other_user_st = str(other.applicant.st_cert_number or "").strip().upper() if other.applicant else ""

            if current_st_cert == other_st or (other_user_st and current_st_cert == other_user_st):
                flags.append({
                    "code": "DUPLICATE_ST_CERTIFICATE",
                    "title": "Duplicate ST Certificate Number Detected",
                    "severity": "HIGH",
                    "points": 45,
                    "description": f"ST Certificate '{current_st_cert}' is already registered in application {other.application_number} ({other.applicant.full_name if other.applicant else 'Unknown'}).",
                    "matched_application_id": other.id,
                    "matched_application_number": other.application_number,
                    "matched_applicant_name": other.applicant.full_name if other.applicant else "Unknown"
                })
                risk_score += 45
                break

    # 2. Check Name + DOB Fuzzy Identity collision across different accounts
    if current_name and current_dob:
        for other in other_apps:
            if other.user_id == user_id:
                continue  # same account
            other_fd = other.form_data or {}
            other_name = str(other_fd.get("full_name", "")).strip()
            other_dob = str(other_fd.get("dob", "")).strip()

            if other_dob and current_dob == other_dob:
                sim = string_similarity(current_name, other_name)
                if sim == 1.0:
                    flags.append({
                        "code": "IDENTICAL_IDENTITY_DIFFERENT_ACCOUNT",
                        "title": "Identical Identity Across Multiple User Accounts",
                        "severity": "HIGH",
                        "points": 40,
                        "description": f"Exact Name '{current_name}' and DOB '{current_dob}' found registered under different account ({other.applicant.email if other.applicant else ''}) in {other.application_number}.",
                        "matched_application_id": other.id,
                        "matched_application_number": other.application_number,
                        "matched_applicant_name": other_name
                    })
                    risk_score += 40
                    break
                elif sim >= 0.85:
                    flags.append({
                        "code": "SUSPECTED_NAME_VARIANT_COLLISION",
                        "title": "Suspected Name Variant & Same DOB",
                        "severity": "HIGH",
                        "points": 35,
                        "description": f"Candidate name '{current_name}' is a close spelling variation ({int(sim*100)}% match) of '{other_name}' with identical DOB '{current_dob}' in application {other.application_number}.",
                        "matched_application_id": other.id,
                        "matched_application_number": other.application_number,
                        "matched_applicant_name": other_name
                    })
                    risk_score += 35
                    break

    # 3. Check Bank Account Collision (DBT diversion fraud signal)
    if current_bank and len(current_bank) >= 6:
        for other in other_apps:
            if other.user_id == user_id:
                continue
            other_fd = other.form_data or {}
            other_bank = str(other_fd.get("bank_account_no", "")).strip()

            if other_bank and current_bank == other_bank:
                flags.append({
                    "code": "SHARED_BANK_ACCOUNT",
                    "title": "Shared Bank Account Number (DBT Risk)",
                    "severity": "HIGH",
                    "points": 45,
                    "description": f"Bank Account '...{current_bank[-4:]}' is linked to another scholar account in application {other.application_number}. DBT guidelines require individual Aadhaar-linked accounts.",
                    "matched_application_id": other.id,
                    "matched_application_number": other.application_number,
                    "matched_applicant_name": other.applicant.full_name if other.applicant else "Unknown"
                })
                risk_score += 45
                break

    # 4. Check Document File Hash Collisions (SHA-256 exact document reuse)
    hashes_to_check = set(uploaded_file_hashes or [])
    if hasattr(application, 'documents') and application.documents:
        for doc in application.documents:
            if doc.file_hash:
                hashes_to_check.add(doc.file_hash)

    if hashes_to_check:
        matching_docs = db.query(Document).filter(
            Document.file_hash.in_(hashes_to_check),
            Document.application_id != current_app_id
        ).all() if current_app_id else []

        if matching_docs:
            for md in matching_docs:
                other_app = md.application
                flags.append({
                    "code": "DUPLICATE_DOCUMENT_HASH",
                    "title": "Exact Document File Reused Across Applications",
                    "severity": "MEDIUM",
                    "points": 25,
                    "description": f"Uploaded document file for '{md.doc_type}' has identical cryptographic hash (SHA-256) to a file in application {other_app.application_number if other_app else 'Other'}.",
                    "matched_application_id": other_app.id if other_app else None,
                    "matched_application_number": other_app.application_number if other_app else "N/A",
                    "matched_applicant_name": other_app.applicant.full_name if other_app and other_app.applicant else "N/A"
                })
                risk_score += 25
                break

    # 5. Check Simultaneous Cross-Scheme Application (NFST + NOS simultaneous)
    if user_id:
        user_other_apps = db.query(Application).filter(
            Application.user_id == user_id,
            Application.id != current_app_id,
            Application.status.in_(["Submitted", "Under Verification", "Scrutiny", "Selected"])
        ).all() if current_app_id else []

        for u_app in user_other_apps:
            if u_app.scheme_id != scheme_id:
                flags.append({
                    "code": "DUAL_SCHEME_SIMULTANEOUS_APPLICATION",
                    "title": "Simultaneous Multi-Scheme Fellowship Application",
                    "severity": "MEDIUM",
                    "points": 30,
                    "description": f"Applicant has concurrently active application ({u_app.application_number} under {u_app.scheme.code if u_app.scheme else 'Scheme'}). Guidelines permit only one active MoTA fellowship.",
                    "matched_application_id": u_app.id,
                    "matched_application_number": u_app.application_number,
                    "matched_applicant_name": application.applicant.full_name if hasattr(application, 'applicant') and application.applicant else "Applicant"
                })
                risk_score += 30
                break

    # Calculate overall risk score & level
    final_score = min(max(round(risk_score, 1), 0.0), 100.0)
    if final_score >= 70.0:
        risk_level = "HIGH"
    elif final_score >= 30.0:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return {
        "risk_score": final_score,
        "risk_level": risk_level,
        "flags_count": len(flags),
        "flags": flags,
        "is_flagged": len(flags) > 0
    }
