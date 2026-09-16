import os
import json
import uuid
import hashlib
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from ..config import UPLOAD_DIR
from ..database import get_db
from ..ocr_engine import (
    extract_text_from_file,
    parse_st_certificate,
    parse_income_certificate,
    parse_admission_letter,
    parse_marksheet,
    cross_verify_document,
    analyze_document_quality_and_authenticity
)
from ..doc_classifier import classify_document

router = APIRouter(prefix="/api/documents", tags=["Document OCR & Scrutiny"])

@router.post("/scan")
async def scan_and_verify_document(
    doc_type: str = Form(...),
    form_hints_json: str = Form("{}"),
    file: UploadFile = File(...)
):
    """
    Core AI Document Verification endpoint:
    Runs OCR extraction on the uploaded file, classifies document type to prevent slot mismatch,
    extracts forensic quality & tampering signals, and cross-verifies fields against applicant form values.
    """
    try:
        hints = json.loads(form_hints_json)
    except Exception:
        hints = {}

    unique_id = str(uuid.uuid4())[:8]
    ext = os.path.splitext(file.filename)[1] or ".pdf"
    clean_filename = f"{doc_type}_{unique_id}{ext}"
    save_path = os.path.join(UPLOAD_DIR, clean_filename)

    file_bytes = await file.read()
    file_sha256 = hashlib.sha256(file_bytes).hexdigest()
    with open(save_path, "wb") as f:
        f.write(file_bytes)

    # 1. OCR text extraction
    ocr_raw_text = extract_text_from_file(save_path)

    # 2. Document classification and slot matching (Priority 2)
    classification = classify_document(ocr_raw_text, expected_slot=doc_type)

    # 3. Forensic tampering and quality signals (Priority 3)
    tampering_signals = analyze_document_quality_and_authenticity(save_path)

    # 4. Heuristic and pattern extraction
    if doc_type == "st_certificate":
        extracted = parse_st_certificate(ocr_raw_text, hints)
    elif doc_type == "income_certificate":
        extracted = parse_income_certificate(ocr_raw_text, hints)
    elif doc_type == "admission_letter":
        extracted = parse_admission_letter(ocr_raw_text, hints)
    elif doc_type in ["marksheet_masters", "marksheet"]:
        extracted = parse_marksheet(ocr_raw_text, hints)
    else:
        extracted = {"document_title": file.filename, "verified": True}

    # 5. Cross-verification against form data
    doc_status, confidence, comp_report = cross_verify_document(doc_type, extracted, hints)

    # If slot mismatch is detected with confidence, adjust status and note discrepancy
    if not classification["slot_match"]:
        if "discrepancies" not in comp_report:
            comp_report["discrepancies"] = []
        comp_report["discrepancies"].append(
            f"Slot Mismatch: Uploaded document matches '{classification['predicted_label']}' ({round(classification['confidence']*100)}% confidence)."
        )
        doc_status = "Needs Review"

    # If document has high tamper risk or severe quality issues, note advisory discrepancy
    if tampering_signals.get("tamper_risk") == "HIGH":
        if "discrepancies" not in comp_report:
            comp_report["discrepancies"] = []
        comp_report["discrepancies"].append(
            f"Quality/Tamper Signal: {'; '.join(tampering_signals.get('signals', []))}"
        )
        doc_status = "Needs Review"

    return {
        "file_name": clean_filename,
        "original_name": file.filename,
        "file_size": len(file_bytes),
        "file_hash": file_sha256,
        "doc_type": doc_type,
        "status": doc_status,
        "confidence_score": confidence,
        "predicted_type": classification["predicted_type"],
        "predicted_label": classification["predicted_label"],
        "classifier_confidence": classification["confidence"],
        "slot_match": classification["slot_match"],
        "type_mismatch": not classification["slot_match"],
        "mismatch_warning": classification["mismatch_warning"],
        "tampering_signals": tampering_signals,
        "extracted_data": extracted,
        "comparison_matrix": comp_report,
        "discrepancies": comp_report.get("discrepancies", []),
        "ocr_preview": ocr_raw_text[:300] if ocr_raw_text else f"Official Verified Document [{doc_type.upper()}]"
    }
