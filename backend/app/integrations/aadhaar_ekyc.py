"""
Aadhaar e-KYC Integration Adapter (Priority 4)
Simulates UIDAI Aadhaar OTP Generation and Demographic e-KYC verification.
Locks verified demographic fields (Full Name, Date of Birth, State) in the application.
"""

import uuid
import re
from typing import Dict, Any, Optional
from datetime import datetime

# UIDAI API Sandbox Gateway Endpoints (Documented for production readiness)
UIDAI_OTP_ENDPOINT = "https://stage1.uidai.gov.in/onlineekyc/getOtp/"
UIDAI_KYC_ENDPOINT = "https://stage1.uidai.gov.in/onlineekyc/getAuth/"

def send_aadhaar_otp(aadhaar_number: str) -> Dict[str, Any]:
    """
    Simulates sending an OTP to the mobile registered with the given 12-digit Aadhaar number.
    Accepts any 12-digit numeric input.
    """
    clean_uid = re.sub(r'[\s\-]', '', str(aadhaar_number))
    if len(clean_uid) != 12 or not clean_uid.isdigit():
        raise ValueError("Invalid Aadhaar number. Must be a 12-digit numerical identifier.")

    txn_id = f"TXN-{uuid.uuid4().hex[:10].upper()}"
    last_four = clean_uid[-4:]

    return {
        "status": "SUCCESS",
        "txn_id": txn_id,
        "masked_aadhaar": f"XXXX-XXXX-{last_four}",
        "message": f"OTP successfully dispatched to registered mobile linked with Aadhaar XXXX-XXXX-{last_four}. (Sandbox Test OTP: 123456)",
        "demo_hint": "Enter 123456 to verify successfully"
    }

def verify_aadhaar_otp(
    txn_id: str,
    otp: str,
    aadhaar_number: str,
    applicant_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Verifies the 6-digit Aadhaar OTP.
    Test OTP '123456' succeeds in prototype/sandbox mode.
    Returns verified demographic identity packet.
    """
    clean_uid = re.sub(r'[\s\-]', '', str(aadhaar_number))
    last_four = clean_uid[-4:] if len(clean_uid) >= 4 else "9901"

    if otp != "123456":
        raise ValueError("Invalid Aadhaar OTP entered. For prototype testing, use test OTP: 123456.")

    verified_name = applicant_name if applicant_name and len(applicant_name.strip()) > 2 else "Birsa Munda"

    return {
        "status": "SUCCESS",
        "is_aadhaar_verified": True,
        "txn_id": txn_id,
        "aadhaar_masked": f"XXXX-XXXX-{last_four}",
        "demographics": {
            "full_name": verified_name,
            "dob": "2001-08-15",
            "gender": "Male",
            "care_of": "Sugana Munda",
            "address": "At: Ulihatu, Block: Khunti, Dist: Ranchi, Jharkhand - 835210",
            "state": "Jharkhand",
            "pincode": "835210",
            "photo_avatar": "https://api.dicebear.com/7.x/bottts/svg?seed=tribal_scholar"
        },
        "locked_fields": ["full_name", "state"],
        "verified_at": datetime.utcnow().isoformat(),
        "notes": "Aadhaar e-KYC demographic cross-check passed. Identity certified via UIDAI authentication server."
    }
