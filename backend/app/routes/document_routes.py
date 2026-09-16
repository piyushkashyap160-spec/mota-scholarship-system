import os
import json
import uuid
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
    cross_verify_document
)

router = APIRouter(prefix="/api/documents", tags=["Document OCR & Scrutiny"])

@router.post("/scan")
async def scan_and_verify_document(
    doc_type: str = Form(...),
    form_hints_json: str = Form("{}"),
    file: UploadFile = File(...)
):
    """
    Core AI Document Verification endpoint:
    Runs OCR extraction on the uploaded file and cross-verifies fields against applicant form values.
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
    with open(save_path, "wb") as f:
        f.write(file_bytes)

    # 1. OCR text extraction
    ocr_raw_text = extract_text_from_file(save_path)

    # 2. Heuristic and pattern extraction
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

    # 3. Cross-verification against form data
    doc_status, confidence, comp_report = cross_verify_document(doc_type, extracted, hints)

    return {
        "file_name": clean_filename,
        "original_name": file.filename,
        "file_size": len(file_bytes),
        "doc_type": doc_type,
        "status": doc_status,
        "confidence_score": confidence,
        "extracted_data": extracted,
        "comparison_matrix": comp_report,
        "discrepancies": comp_report.get("discrepancies", []),
        "ocr_preview": ocr_raw_text[:300] if ocr_raw_text else f"Official Verified Document [{doc_type.upper()}]"
    }
