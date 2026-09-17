"""
MoTA Document Classifier Engine (Priority 2)
Trained on synthetic samples of authentic Indian government and academic document text.
Classifies uploaded documents to prevent and flag wrong-slot uploads.
"""

import os
import re
import pickle
from typing import Dict, Any, Tuple, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

MODEL_PATH = os.path.join(os.path.dirname(__file__), "doc_classifier_model.pkl")

# Document class labels
DOC_LABELS = [
    "st_certificate",
    "income_certificate",
    "admission_letter",
    "marksheet",
    "bank_passbook",
    "aadhaar_card",
    "unknown"
]

FRIENDLY_NAMES = {
    "st_certificate": "Scheduled Tribe (ST) Certificate",
    "income_certificate": "Income Certificate / Salary Certificate",
    "admission_letter": "University Admission / Offer Letter",
    "marksheet": "Academic Marksheet / Transcript",
    "bank_passbook": "Bank Passbook / Cancelled Cheque",
    "aadhaar_card": "Aadhaar Card (UIDAI)",
    "unknown": "Unrecognized Document"
}

# Rich synthetic dataset representing authentic Indian documentation patterns
SYNTHETIC_DATA = [
    # --- ST CERTIFICATES ---
    ("st_certificate", "GOVERNMENT OF JHARKHAND Office of the Sub-Divisional Officer Caste Certificate Scheduled Tribe Certificate Form of Caste Certificate for Scheduled Tribes This is to certify that belongs to Santhal community which is recognized as a Scheduled Tribe under The Constitution (Scheduled Tribes) Order 1950 issued by Tehsildar Sub-Divisional Magistrate"),
    ("st_certificate", "GOVERNMENT OF ODISHA Office of the Tahasildar Caste Certificate ST Certificate Scheduled Tribe Certificate Shri Smt son daughter of village post police station district belongs to Gond tribe recognized as Scheduled Tribe under Constitution Scheduled Tribes Union Territories Order 1951"),
    ("st_certificate", "OFFICE OF THE DISTRICT MAGISTRATE MADHYA PRADESH Scheduled Tribe Certificate This is to certify that resident of Tehsil District belongs to Bhil tribe which is recognized as a Scheduled Tribe under the Constitution (Scheduled Tribes) Order 1950 as amended by the Scheduled Castes and Scheduled Tribes Orders Amendment Act 1976"),
    ("st_certificate", "GOVERNMENT OF MAHARASHTRA Sub-Divisional Officer Revenue Department Scheduled Tribe Certificate Caste Certificate Certificate No SDO/ST/2022/4921 Issuing Authority Tehsildar Community Bodo Munda Scheduled Tribe category valid for education scholarship"),
    ("st_certificate", "Scheduled Tribe Certificate SDO Office Jharkhand Community Ho Oraon Santhal Scheduled Tribe Order 1950 Revenue Circle Officer District Collectorate Official Seal and Signature"),
    ("st_certificate", "Government of Rajasthan Office of Sub-Divisional Magistrate ST Caste Certificate Scheduled Tribe Mina Meena Bhil Garasia tribe Constitution Scheduled Tribe Order revenue seal"),
    ("st_certificate", "Government of Chhattisgarh Tahsil Office Scheduled Tribe Certificate Gond Maria Muria Bhattra Halba community Scheduled Tribe certificate number revenue officer seal"),

    # --- INCOME CERTIFICATES ---
    ("income_certificate", "GOVERNMENT OF JHARKHAND Revenue and Land Reforms Department Income Certificate Office of the Circle Officer Tehsildar Annual Income Certificate Gross annual family income from all sources including agriculture business and salary is Rs Rupees per annum Financial Year 2024-2025 issued for scholarship purpose"),
    ("income_certificate", "OFFICE OF THE TAHSILDAR ODISHA Revenue Department Annual Income Certificate Certified that the gross annual family income of Shri Smt father mother from all sources does not exceed Rupees Three Lakhs Fifty Thousand only per annum as per enquiry report"),
    ("income_certificate", "FORM 16 Part A and Part B Certificate under section 203 of the Income-tax Act 1961 for tax deducted at source from income chargeable under the head Salaries Employee PAN Employer TAN Gross Salary Deduction under Chapter VI-A Total Income Tax Payable"),
    ("income_certificate", "SALARY SLIP Pay Slip for the Month of Basic Pay Dearness Allowance DA House Rent Allowance HRA Gross Earnings Net Pay Deductions Provident Fund PF Professional Tax Employer Name Designation Employee ID"),
    ("income_certificate", "Revenue Department Government of Maharashtra Tahsildar Office Income Certificate Annual Family Income from all sources is Rs 2,40,000 Rupees Two Lakh Forty Thousand only Certificate Valid for Financial Year"),
    ("income_certificate", "Competent Revenue Authority Income Certificate Annual income certificate for post-matric scholarship scheme applicant family income verification tehsildar stamp"),
    ("income_certificate", "Form 16 Salary Certificate Employer monthly pay slip annual gross salary total taxable income TDS deduction Form 16 Part A Assessment Year"),

    # --- ADMISSION LETTERS ---
    ("admission_letter", "INDIAN INSTITUTE OF TECHNOLOGY Academic Affairs Section Office of Dean Provisional Offer of Admission Ph.D. Programme Doctor of Philosophy Research Scholar Academic Session 2025-2026 Department of Computer Science and Engineering You have been provisionally selected for admission Registration fee Tuition fee Enrolment No"),
    ("admission_letter", "UNIVERSITY INSTITUTE OF TECHNOLOGY Dean Academic Admissions Provisional Admission Letter Offer of Admission for Postgraduate Studies M.Tech Master of Science Research Fellow Roll Number Department Faculty Supervisor Letter of acceptance registration date orientation semester fees"),
    ("admission_letter", "UNIVERSITY OF OXFORD / CAMBRIDGE / IMPERIAL COLLEGE LONDON Confirmation of Acceptance for Studies CAS Statement Unconditional Offer Letter Postgraduate Admissions MSc PhD Research Programme Tuition Fees Academic Year Visa Sponsorship Confirmation student ID"),
    ("admission_letter", "CENTRAL UNIVERSITY OF JHARKHAND Office of Admissions Provisional Admission Offer Letter Candidate has been offered admission into Ph.D. Tribal Studies / Anthropology Academic Year 2025 semester registration enrollment number"),
    ("admission_letter", "Foreign University Offer of Admission International Graduate School Doctoral Programme Ph.D. fellowship admission offer letter tuition waiver supervisor confirmation"),

    # --- MARKSHEETS ---
    ("marksheet", "CENTRAL BOARD OF SECONDARY EDUCATION CBSE Statement of Marks Senior School Certificate Examination Marks Statement Subject Code English Physics Chemistry Mathematics Total Marks Maximum Marks 500 Percentage Grade Point CGPA Result PASS Controller of Examinations"),
    ("marksheet", "DELHI UNIVERSITY Statement of Marks Transcript of Records Master of Science M.Sc. Semester Examination Semester I II III IV Total Credits Grade Points SGPA CGPA Cumulative Grade Point Average First Class with Distinction Controller of Examinations"),
    ("marksheet", "JAWAHARLAL NEHRU UNIVERSITY JNU Consolidated Grade Sheet Statement of Grades Transcript Master of Arts M.A. M.Phil Degree Course Code Course Title Credits Grade Letter Grade Point Average Semester Final Result Promoted"),
    ("marksheet", "State Board of Technical Education Consolidated Marksheet Bachelor of Technology Degree Examination Semester Marks Internal Marks External Marks Total Marks Percentage 78.5% Division First Class Passed Controller of Examination"),
    ("marksheet", "University Marks Statement Transcript Bachelor of Science Consolidated Statement of Marks Marks Obtained Maximum Marks Grade SGPA CGPA Final Result First Division"),

    # --- BANK PASSBOOKS ---
    ("bank_passbook", "STATE BANK OF INDIA SBI Savings Bank Account Passbook Branch Code IFSC Code SBIN0001234 Account Number MICR Code CIF Number Customer Name Account Holder Joint Account Address Branch Manager Seal Signature Cheque Book Issued Direct Benefit Transfer DBT enabled"),
    ("bank_passbook", "PUNJAB NATIONAL BANK PNB Savings Account Passbook Account No IFSC Code PUNB0123450 Account Holder Name Father Name CIF ID Nominee Registered Branch Address Transaction Date Debit Credit Balance"),
    ("bank_passbook", "CANCELLED CHEQUE Bank of Baroda Pay Rupee A/C Payee Only Account Number IFSC BARB0MAINXX Cheque Number MICR Signatory Valid for Direct Benefit Transfer DBT Mandate"),
    ("bank_passbook", "CANARA BANK Passbook Savings Bank A/c IFSC CNRB0002145 Account Number Branch IFSC MICR Name of Account Holder Bank seal and authorized signature for DBT PFMS"),
    ("bank_passbook", "Savings Bank Passbook cancelled cheque IFSC code account number customer ID bank statement branch name account holder passbook first page copy"),

    # --- AADHAAR CARDS ---
    ("aadhaar_card", "GOVERNMENT OF INDIA UNIQUE IDENTIFICATION AUTHORITY OF INDIA UIDAI Mera Aadhaar Meri Pehchan Aadhaar is proof of identity not of citizenship To Shri/Smt Father Name DOB Date of Birth Gender Male Female Address Enrollment Number VID Aadhaar Number help@uidai.gov.in www.uidai.gov.in 1947"),
    ("aadhaar_card", "Unique Identification Authority of India UIDAI Government of India Download Date Issue Date Aadhaar Card Aadhaar No Address S/O D/O W/O Enrolment No VID Male Female Mera Aadhaar Meri Pehchan"),
    ("aadhaar_card", "Aadhaar Card UIDAI Government of India Year of Birth YOB Gender Mobile Number Linked Address QR Code Unique Identification Number"),

    # --- UNKNOWN / GENERAL ---
    ("unknown", "Invoice Bill Receipt Total Amount GST Tax Number Item Quantity Price Thank you for your purchase Delivery address Customer copy"),
    ("unknown", "Electricity Bill Power Distribution Corporation Consumer Number Units Consumed Meter Reading Due Date Amount Payable Disconnection Notice"),
    ("unknown", "Railway Ticket IRCTC Electronic Reservation Slip ERS PNR Number Train Number Departure Time Arrival Time Passenger Name Age Berth Coach Confirmed"),
    ("unknown", "Random text document lorem ipsum dolor sit amet notes meeting minutes agenda general announcement notice board newspaper article")
]

_CLASSIFIER_PIPELINE: Optional[Pipeline] = None

def train_and_save_classifier() -> Pipeline:
    """Trains a TF-IDF + MultinomialNB classifier on synthetic training data and caches it."""
    texts = [item[1] for item in SYNTHETIC_DATA]
    labels = [item[0] for item in SYNTHETIC_DATA]

    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(ngram_range=(1, 2), max_features=2500, lowercase=True)),
        ('clf', MultinomialNB(alpha=0.1))
    ])

    pipeline.fit(texts, labels)

    try:
        with open(MODEL_PATH, "wb") as f:
            pickle.dump(pipeline, f)
    except Exception as e:
        # If write fails (e.g. read-only permissions), model still works in-memory
        pass

    return pipeline

def get_classifier() -> Pipeline:
    """Returns the cached or newly trained classifier pipeline."""
    global _CLASSIFIER_PIPELINE
    if _CLASSIFIER_PIPELINE is not None:
        return _CLASSIFIER_PIPELINE

    if os.path.exists(MODEL_PATH):
        try:
            with open(MODEL_PATH, "rb") as f:
                _CLASSIFIER_PIPELINE = pickle.load(f)
                return _CLASSIFIER_PIPELINE
        except Exception:
            pass

    # Train fresh
    _CLASSIFIER_PIPELINE = train_and_save_classifier()
    return _CLASSIFIER_PIPELINE

def normalize_slot_type(slot_name: str) -> str:
    """Maps various form slot keys to canonical document class types."""
    if not slot_name:
        return "unknown"
    s = slot_name.lower().strip()
    if "st_cert" in s or "caste" in s or "tribe" in s:
        return "st_certificate"
    if "income" in s or "salary" in s or "form16" in s or "form_16" in s:
        return "income_certificate"
    if "admission" in s or "offer" in s or "bonafide" in s:
        return "admission_letter"
    if "mark" in s or "transcript" in s or "degree" in s:
        return "marksheet"
    if "bank" in s or "passbook" in s or "cheque" in s:
        return "bank_passbook"
    if "aadhaar" in s or "uid" in s or "identity" in s:
        return "aadhaar_card"
    return "unknown"

def classify_document(ocr_text: str, expected_slot: Optional[str] = None) -> Dict[str, Any]:
    """
    Classifies OCR text into one of the 7 document categories.
    Compares predicted category with the expected slot name.

    Returns:
      {
        "predicted_type": str,
        "predicted_label": str,
        "confidence": float,
        "slot_match": bool,
        "mismatch_warning": Optional[str],
        "probabilities": dict
      }
    """
    if not ocr_text or len(ocr_text.strip()) < 15:
        norm_expected = normalize_slot_type(expected_slot) if expected_slot else "unknown"
        return {
            "predicted_type": norm_expected if norm_expected != "unknown" else "unknown",
            "predicted_label": FRIENDLY_NAMES.get(norm_expected, "Unknown"),
            "confidence": 0.50,
            "slot_match": True,
            "mismatch_warning": None,
            "probabilities": {cls: 0.14 for cls in DOC_LABELS}
        }

    clf = get_classifier()

    # Probability distribution
    probs = clf.predict_proba([ocr_text])[0]
    prob_dict = {str(cls): round(float(prob), 4) for cls, prob in zip(clf.classes_, probs)}

    # High-confidence keyword heuristics that override or reinforce ML
    text_lower = ocr_text.lower()
    
    # ST Certificate strong signals
    if ("scheduled tribe" in text_lower or "constitution (scheduled tribes)" in text_lower) and "caste" in text_lower:
        prob_dict["st_certificate"] = max(prob_dict.get("st_certificate", 0), 0.94)

    # Aadhaar strong signals
    if "uidai" in text_lower or "mera aadhaar" in text_lower or "unique identification authority" in text_lower:
        prob_dict["aadhaar_card"] = max(prob_dict.get("aadhaar_card", 0), 0.96)

    # Bank passbook strong signals
    if ("ifsc" in text_lower and "account no" in text_lower) or "passbook" in text_lower or "cancelled cheque" in text_lower:
        prob_dict["bank_passbook"] = max(prob_dict.get("bank_passbook", 0), 0.92)

    # Income certificate strong signals
    if ("annual income" in text_lower or "gross annual family income" in text_lower or "form 16" in text_lower) and "revenue" in text_lower:
        prob_dict["income_certificate"] = max(prob_dict.get("income_certificate", 0), 0.91)

    # Admission letter strong signals
    if "offer of admission" in text_lower or "provisional admission" in text_lower or "academic session" in text_lower:
        prob_dict["admission_letter"] = max(prob_dict.get("admission_letter", 0), 0.90)

    # Marksheet strong signals
    if "statement of marks" in text_lower or "cumulative grade point" in text_lower or "cgpa" in text_lower or "marksheet" in text_lower:
        prob_dict["marksheet"] = max(prob_dict.get("marksheet", 0), 0.92)

    # Pick top class
    best_class = str(max(prob_dict, key=prob_dict.get))
    confidence = round(float(prob_dict[best_class]), 2)

    # Evaluate slot match
    norm_expected = normalize_slot_type(expected_slot) if expected_slot else "unknown"

    slot_match = True
    mismatch_warning = None

    if norm_expected != "unknown" and best_class != "unknown" and best_class != norm_expected:
        # If confidence in the differing class is high (>= 0.60), flag slot mismatch
        if confidence >= 0.60:
            slot_match = False
            expected_friendly = FRIENDLY_NAMES.get(norm_expected, norm_expected.replace('_', ' ').title())
            predicted_friendly = FRIENDLY_NAMES.get(best_class, best_class.replace('_', ' ').title())
            mismatch_warning = (
                f"You uploaded what appears to be a {predicted_friendly} into the {expected_friendly} slot. "
                f"Please verify you selected the correct file before submitting."
            )

    return {
        "predicted_type": best_class,
        "predicted_label": FRIENDLY_NAMES.get(best_class, best_class.title()),
        "confidence": confidence,
        "slot_match": slot_match,
        "mismatch_warning": mismatch_warning,
        "probabilities": prob_dict
    }

def _ensure_model_trained() -> None:
    """
    Checks if doc_classifier_model.pkl exists on disk (e.g. after a fresh clone).
    If missing, generates synthetic training data and trains + saves the model automatically.
    """
    if not os.path.exists(MODEL_PATH):
        try:
            train_and_save_classifier()
        except Exception:
            pass

# Ensure classifier model exists on module import
_ensure_model_trained()

if __name__ == "__main__":
    train_and_save_classifier()
    print("Document classifier trained and cached successfully.")
    sample = "Office of the Tahasildar Scheduled Tribe Certificate Gond community Constitution Scheduled Tribe Order 1950"
    res = classify_document(sample, expected_slot="income_certificate")
    print("Test Sample Classification:", res)
