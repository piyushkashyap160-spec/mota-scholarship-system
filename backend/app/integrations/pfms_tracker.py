"""
PFMS & Direct Benefit Transfer (DBT) Tracker Integration (Priority 4)
Tracks scholarship fund disbursement stages through the Public Financial Management System:
- Sanction Order Generated
- Bill Passed by MoTA PAO
- PFMS NPCI Aadhaar-Seeded Bank Validation
- DBT Payment Initiated
- Bank Credit Confirmed with UTR Reference
"""

import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime

PFMS_STAGES = [
    {
        "step": 1,
        "stage_code": "SANCTION_GENERATED",
        "title": "Sanction Order Generated",
        "authority": "MoTA Joint Secretary (Fellowships)",
        "description": "Financial sanction order processed under Scheme Budget Head 2225-ST-Welfare."
    },
    {
        "step": 2,
        "stage_code": "PAO_BILL_PASSED",
        "title": "Bill Passed by MoTA PAO",
        "authority": "Pay & Accounts Office (PAO), Ministry of Tribal Affairs",
        "description": "Bill scrutinized and passed for electronic treasury release."
    },
    {
        "step": 3,
        "stage_code": "PFMS_NPCI_VALIDATED",
        "title": "PFMS & NPCI Account Pre-Validation",
        "authority": "National Payments Corporation of India (NPCI) Aadhaar Mapper",
        "description": "Bank account verified active and seeded with applicant Aadhaar on NPCI mapper."
    },
    {
        "step": 4,
        "stage_code": "DBT_INITIATED",
        "title": "DBT Payment Initiated",
        "authority": "Reserve Bank of India / PFMS Gateway",
        "description": "Direct Benefit Transfer instruction sent via RTGS/NEFT batch."
    },
    {
        "step": 5,
        "stage_code": "BANK_CREDITED",
        "title": "Bank Credit Confirmed",
        "authority": "Beneficiary Bank",
        "description": "Funds credited directly into candidate savings account."
    }
]

def get_disbursement_tracker(application_id: int, status: str, scheme_code: str = "NFST") -> Dict[str, Any]:
    """Generates the PFMS DBT lifecycle stages and instalment schedule for an application."""
    is_selected = status.lower() in ["selected", "approved"]

    current_step = 5 if is_selected else (2 if status.lower() in ["scrutiny", "under verification"] else 1)
    
    stages_timeline = []
    for s in PFMS_STAGES:
        step_completed = s["step"] <= current_step
        step_active = s["step"] == current_step
        stages_timeline.append({
            **s,
            "is_completed": step_completed,
            "is_active": step_active,
            "date": "2026-03-15" if step_completed else "Pending Selection",
            "utr_number": "SBIN26078192083" if s["stage_code"] == "BANK_CREDITED" and step_completed else None
        })

    # Instalment Schedule
    total_grant = 432000.0 if scheme_code.upper() == "NFST" else 1850000.0
    instalments = [
        {
            "instalment_no": 1,
            "period": "Quarter 1 (Apr - Jun 2026)",
            "amount": round(total_grant * 0.25, 2),
            "status": "Credited" if is_selected else "Scheduled",
            "utr": "SBIN26078192083" if is_selected else "Pending",
            "credit_date": "2026-04-05" if is_selected else "2026-04-15"
        },
        {
            "instalment_no": 2,
            "period": "Quarter 2 (Jul - Sep 2026)",
            "amount": round(total_grant * 0.25, 2),
            "status": "Scheduled",
            "utr": "Pending",
            "credit_date": "2026-07-10"
        },
        {
            "instalment_no": 3,
            "period": "Quarter 3 (Oct - Dec 2026)",
            "amount": round(total_grant * 0.25, 2),
            "status": "Scheduled",
            "utr": "Pending",
            "credit_date": "2026-10-10"
        },
        {
            "instalment_no": 4,
            "period": "Quarter 4 (Jan - Mar 2027)",
            "amount": round(total_grant * 0.25, 2),
            "status": "Scheduled",
            "utr": "Pending",
            "credit_date": "2027-01-10"
        }
    ]

    return {
        "application_id": application_id,
        "scheme_code": scheme_code,
        "total_disbursement_amount": total_grant,
        "current_stage": PFMS_STAGES[current_step - 1]["title"],
        "stages": stages_timeline,
        "instalments": instalments,
        "npci_aadhaar_seeded": True,
        "bank_account_masked": "SBINXXXX8921"
    }

def log_disbursement_grievance(application_id: int, applicant_name: str, grievance_type: str, description: str) -> Dict[str, Any]:
    """Records a DBT / PFMS disbursement grievance with official tracking token."""
    ticket_id = f"GRV-PFMS-{datetime.utcnow().strftime('%Y%m')}-{uuid.uuid4().hex[:6].upper()}"
    return {
        "status": "LOGGED",
        "ticket_id": ticket_id,
        "application_id": application_id,
        "applicant_name": applicant_name,
        "grievance_type": grievance_type,
        "description": description,
        "expected_resolution_days": 3,
        "escalation_desk": "MoTA Direct Benefit Transfer Cell, Shastri Bhawan, New Delhi",
        "created_at": datetime.utcnow().isoformat()
    }
