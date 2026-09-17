"""
MoTA Scholarship & Fellowship Management System - Master Seed Data
Sourced with authentic statutory rules, quotas, income ceilings, and document specifications from:
- tribal.nic.in (Ministry of Tribal Affairs)
- dbttribal.gov.in (MoTA DBT Portal)
- fellowship.tribal.gov.in (NFST Portal)
- overseas.tribal.gov.in (NOS Portal)
- scholarships.gov.in (National Scholarship Portal)
"""

from datetime import datetime, timedelta
import hashlib
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from .models import User, Scheme, Application, Document, Deficiency, ActivityLog, AuditLogEntry
from .auth import get_password_hash
from .ocr_engine import cross_verify_document, parse_st_certificate, parse_income_certificate, parse_admission_letter, parse_marksheet
from .eligibility_engine import evaluate_eligibility
from .merit_engine import calculate_merit_score
from .fraud_engine import evaluate_application_risk
from .audit import log_action, verify_chain_integrity

ALL_INDIAN_STATES_AND_UTS = [
    "Andaman and Nicobar Islands",
    "Andhra Pradesh",
    "Arunachal Pradesh",
    "Assam",
    "Bihar",
    "Chandigarh",
    "Chhattisgarh",
    "Dadra and Nagar Haveli and Daman and Diu",
    "Delhi (NCT)",
    "Goa",
    "Gujarat",
    "Haryana",
    "Himachal Pradesh",
    "Jammu and Kashmir",
    "Jharkhand",
    "Karnataka",
    "Kerala",
    "Ladakh",
    "Lakshadweep",
    "Madhya Pradesh",
    "Maharashtra",
    "Manipur",
    "Meghalaya",
    "Mizoram",
    "Nagaland",
    "Odisha",
    "Puducherry",
    "Punjab",
    "Rajasthan",
    "Sikkim",
    "Tamil Nadu",
    "Telangana",
    "Tripura",
    "Uttar Pradesh",
    "Uttarakhand",
    "West Bengal"
]

def seed_database(db: Session, force: bool = False):
    if not force and db.query(Scheme).first() is not None and db.query(User).first() is not None:
        return

    if force:
        print("Clearing existing records for fresh reseed...")
        db.query(AuditLogEntry).delete()
        db.query(ActivityLog).delete()
        db.query(Deficiency).delete()
        db.query(Document).delete()
        db.query(Application).delete()
        db.query(Scheme).delete()
        db.query(User).delete()
        db.commit()

    print("Seeding MoTA Scholarship & Fellowship database with real data from tribal.nic.in & dbttribal.gov.in...")

    # -------------------------------------------------------------------------
    # 1. ADMIN USER
    # -------------------------------------------------------------------------
    admin = User(
        email="admin@mota.gov.in",
        hashed_password=get_password_hash("admin123"),
        role="admin",
        full_name="Dr. R. K. Soren, IAS (Joint Secretary - MoTA)",
        phone="+91-11-2338-8480",
        state="New Delhi",
        community_tribe="Santhal",
        institution="Ministry of Tribal Affairs, Shastri Bhawan",
        course="Administrative Division"
    )
    db.add(admin)
    db.flush()

    # -------------------------------------------------------------------------
    # 2. SCHEME 1: NFST (National Fellowship for Scheduled Tribes)
    # Portal: https://fellowship.tribal.gov.in/
    # Total Slots: 750 slots/year | Disbursement: DBT via Canara Bank
    # -------------------------------------------------------------------------
    nfst = Scheme(
        code="NFST",
        name="NFST - National Fellowship for Scheduled Tribes",
        full_title="National Fellowship and Scholarship for Higher Education of ST Students (Fellowship for M.Phil / Ph.D in India)",
        objective="To provide financial assistance to Scheduled Tribe (ST) students to pursue higher studies like M.Phil and Ph.D in recognized Indian Universities and Institutes.",
        financial_assistance="M.Phil fellowship @ ₹25,000/month; Ph.D fellowship @ ₹28,000/month plus contingency allowance and HRA as per UGC norms.",
        target_group="Scheduled Tribe (ST) Research Scholars in India (750 slots/year)",
        income_ceiling=600000.0,
        min_marks=55.0,
        is_active=True,
        required_documents=[
            {
                "doc_type": "st_certificate",
                "title": "Scheduled Tribe (ST) Caste Certificate",
                "description": "Valid ST certificate issued by Sub-Divisional Magistrate / Tehsildar / Competent Authority.",
                "required": True,
                "target_fields": ["name", "caste", "certificate_number", "issuing_authority", "issue_date"]
            },
            {
                "doc_type": "income_certificate",
                "title": "Annual Family Income Certificate",
                "description": "Income certificate certifying total annual family income from all sources <= ₹6,00,000.",
                "required": True,
                "target_fields": ["name", "annual_income", "issuing_authority", "issue_date"]
            },
            {
                "doc_type": "marksheet_masters",
                "title": "Master's Degree Marksheet",
                "description": "Transcript/marksheet of qualifying Master's degree with minimum 55% marks.",
                "required": True,
                "target_fields": ["name", "university", "course", "percentage", "year_of_passing"]
            },
            {
                "doc_type": "admission_letter",
                "title": "Admission / Enrollment Letter",
                "description": "Proof of registration or admission letter in an accredited Indian University/Institute.",
                "required": True,
                "target_fields": ["name", "institution", "course", "enrollment_date"]
            },
            {
                "doc_type": "bank_passbook",
                "title": "Bank Passbook First Page",
                "description": "Aadhaar-seeded bank account passbook copy showing bank name, account number, and IFSC.",
                "required": True,
                "target_fields": ["account_holder_name", "account_number", "ifsc_code", "bank_name"]
            },
            {
                "doc_type": "aadhaar_card",
                "title": "Aadhaar Card",
                "description": "Applicant's official Aadhaar card issued by UIDAI.",
                "required": True,
                "target_fields": ["name", "dob", "aadhaar_number", "address"]
            },
            {
                "doc_type": "disability_certificate",
                "title": "Disability Certificate (Divyangjan)",
                "description": "Valid disability certificate if applying under Divyangjan quota.",
                "required": False,
                "target_fields": ["name", "disability_type", "percentage", "issuing_authority"]
            }
        ],
        eligibility_rules={
            "scheme_id": "NFST",
            "portal": "https://fellowship.tribal.gov.in/",
            "category_required": "ST",
            "income_ceiling": 600000.0,
            "qualifying_exam": "Master's Degree",
            "min_qualifying_percentage": 55.0,
            "selection_mode": "Merit based on Master's Degree marks",
            "preferred_groups": ["Girls", "Divyangjan", "PVTG"],
            "eligible_institutions": [
                "UGC 2(f)/12(B)",
                "Deemed Universities UGC Section 3",
                "Central/State Govt funded institutions",
                "Institutes of National Importance"
            ],
            "eligible_courses": ["MPhil", "PhD", "M.Phil", "Ph.D", "Doctorate"],
            "total_slots_per_year": 750,
            "disbursement_channel": "DBT via Canara Bank"
        },
        merit_weights={
            "marks_weight": 0.70,
            "income_weight": 0.30,
            "female_bonus": 5.0,
            "pvtg_bonus": 5.0,
            "divyangjan_bonus": 3.0
        },
        form_fields=[
            {"id": "full_name", "label": "Full Name (as on ST Certificate)", "type": "text", "required": True, "section": "Personal Info"},
            {"id": "father_name", "label": "Father's / Guardian's Name", "type": "text", "required": True, "section": "Personal Info"},
            {"id": "gender", "label": "Gender", "type": "select", "options": ["Male", "Female", "Other"], "required": True, "section": "Personal Info"},
            {"id": "dob", "label": "Date of Birth", "type": "date", "required": True, "section": "Personal Info"},
            {"id": "phone", "label": "Mobile Number", "type": "tel", "required": True, "section": "Personal Info"},
            {"id": "state", "label": "Domicile State", "type": "select", "options": ALL_INDIAN_STATES_AND_UTS, "required": True, "section": "Tribal Verification"},
            {"id": "community_tribe", "label": "Sub-Caste / Tribe Name", "type": "text", "required": True, "section": "Tribal Verification"},
            {"id": "st_cert_number", "label": "ST Certificate Number", "type": "text", "required": True, "section": "Tribal Verification"},
            {"id": "category", "label": "Category", "type": "text", "required": True, "default": "ST", "read_only": True, "section": "Tribal Verification"},
            {"id": "is_pvtg", "label": "Belongs to Particularly Vulnerable Tribal Group (PVTG)?", "type": "select", "options": ["No", "Yes"], "required": True, "section": "Tribal Verification"},
            {"id": "is_divyangjan", "label": "Person with Benchmark Disability (Divyangjan)?", "type": "select", "options": ["No", "Yes"], "required": True, "section": "Personal Info"},
            {"id": "course", "label": "Research Program", "type": "select", "options": ["Ph.D", "M.Phil"], "required": True, "section": "Academic Details"},
            {"id": "institution", "label": "Admitted Institution / University", "type": "text", "required": True, "section": "Academic Details"},
            {"id": "institution_type", "label": "Institution Category", "type": "select", "options": ["Institutes of National Importance", "Central University", "State Govt Funded Institution", "Deemed University UGC Sec 3", "UGC 2(f)/12(B)"], "required": True, "section": "Academic Details"},
            {"id": "research_topic", "label": "Proposed Research Topic", "type": "textarea", "required": True, "section": "Academic Details"},
            {"id": "marks_percentage", "label": "Master's Degree Aggregate Percentage (%)", "type": "number", "required": True, "section": "Academic Details"},
            {"id": "annual_income", "label": "Annual Family Income from all sources (INR ₹)", "type": "number", "required": True, "section": "Financial & Bank Info"},
            {"id": "bank_account_no", "label": "Aadhaar-Linked Bank Account Number", "type": "text", "required": True, "section": "Financial & Bank Info"},
            {"id": "bank_ifsc", "label": "Bank IFSC Code", "type": "text", "required": True, "section": "Financial & Bank Info"},
            {"id": "bank_name", "label": "Bank Name & Branch", "type": "text", "required": True, "section": "Financial & Bank Info"}
        ]
    )
    db.add(nfst)

    # -------------------------------------------------------------------------
    # 3. SCHEME 2: NOS (National Overseas Scholarship)
    # Portal: https://overseas.tribal.gov.in/
    # Total Slots: 20 slots/year (17 ST + 3 PVTG reserved)
    # -------------------------------------------------------------------------
    nos = Scheme(
        code="NOS",
        name="NOS - National Overseas Scholarship",
        full_title="National Overseas Scholarship Scheme for Scheduled Tribe Candidates for Higher Studies Abroad (Master's / Ph.D. / Post-Doctoral)",
        objective="To facilitate low-income Scheduled Tribe scholars in obtaining Master's, Ph.D. degrees, and Post-Doctoral research from top accredited global universities abroad.",
        financial_assistance="Annual maintenance: USD 15,400 + contingency: USD 1,532 + tuition fee, poll tax, visa fee, medical insurance, airfare, and journey expenses.",
        target_group="Scheduled Tribe (ST) Scholars Pursuing Studies Abroad (20 slots: 17 ST + 3 PVTG)",
        income_ceiling=600000.0,
        min_marks=55.0,
        is_active=True,
        required_documents=[
            {
                "doc_type": "st_certificate",
                "title": "ST Caste Certificate with English Translation",
                "description": "Valid ST certificate issued by competent authority with official seal.",
                "required": True,
                "target_fields": ["name", "caste", "certificate_number", "issuing_authority", "issue_date"]
            },
            {
                "doc_type": "income_certificate",
                "title": "Family Income Certificate",
                "description": "Proof certifying total family income <= ₹6,00,000 per annum.",
                "required": True,
                "target_fields": ["name", "annual_income", "issuing_authority", "issue_date"]
            },
            {
                "doc_type": "marksheet_masters",
                "title": "Bachelor's / Master's Marksheet",
                "description": "Qualifying degree transcripts with minimum 55% marks.",
                "required": True,
                "target_fields": ["name", "university", "course", "percentage", "year_of_passing"]
            },
            {
                "doc_type": "admission_letter",
                "title": "Admission Letter from Foreign University",
                "description": "Offer/admission letter from a recognized overseas institution.",
                "required": True,
                "target_fields": ["name", "university", "country", "course", "start_date"]
            },
            {
                "doc_type": "passport",
                "title": "Valid Indian Passport",
                "description": "Scanned copy of bio-data pages of valid Indian Passport.",
                "required": True,
                "target_fields": ["name", "passport_number", "dob", "expiry_date", "nationality"]
            },
            {
                "doc_type": "bank_passbook",
                "title": "Bank Passbook First Page",
                "description": "Bank passbook for processing initial travel/contingency advance.",
                "required": True,
                "target_fields": ["account_holder_name", "account_number", "ifsc_code", "bank_name"]
            },
            {
                "doc_type": "aadhaar_card",
                "title": "Aadhaar Card",
                "description": "Aadhaar card for biometric/demographic verification.",
                "required": True,
                "target_fields": ["name", "dob", "aadhaar_number", "address"]
            },
            {
                "doc_type": "medical_certificate",
                "title": "Medical Fitness Certificate",
                "description": "Fitness certificate issued by a registered medical practitioner.",
                "required": True,
                "target_fields": ["name", "issuing_doctor", "date", "fitness_status"]
            }
        ],
        eligibility_rules={
            "scheme_id": "NOS",
            "portal": "https://overseas.tribal.gov.in/",
            "category_required": "ST",
            "income_ceiling": 600000.0,
            "min_qualifying_percentage": 55.0,
            "eligible_courses": ["Post Graduation", "Master's", "Ph.D", "PhD", "Post-Doctoral", "M.S."],
            "selection_mode": "Interview-based merit list by Expert Committee (2 years window for foreign admission)",
            "total_slots_per_year": 20,
            "pvtg_reserved_slots": 3,
            "disbursement_channel": "Through Indian Missions abroad via Ministry of External Affairs, reimbursed by MoTA"
        },
        merit_weights={
            "marks_weight": 0.60,
            "interview_weight": 0.30,
            "pvtg_bonus": 5.0,
            "female_bonus": 5.0
        },
        form_fields=[
            {"id": "full_name", "label": "Full Name (as per Passport)", "type": "text", "required": True, "section": "Personal Info"},
            {"id": "father_name", "label": "Father's / Mother's Name", "type": "text", "required": True, "section": "Personal Info"},
            {"id": "gender", "label": "Gender", "type": "select", "options": ["Male", "Female", "Other"], "required": True, "section": "Personal Info"},
            {"id": "dob", "label": "Date of Birth", "type": "date", "required": True, "section": "Personal Info"},
            {"id": "phone", "label": "Mobile Number", "type": "tel", "required": True, "section": "Personal Info"},
            {"id": "passport_number", "label": "Indian Passport Number", "type": "text", "required": True, "section": "Passport Details"},
            {"id": "passport_expiry_date", "label": "Passport Expiry Date", "type": "date", "required": True, "section": "Passport Details"},
            {"id": "state", "label": "Native State", "type": "select", "options": ALL_INDIAN_STATES_AND_UTS, "required": True, "section": "Tribal Verification"},
            {"id": "community_tribe", "label": "Tribal Community", "type": "text", "required": True, "section": "Tribal Verification"},
            {"id": "st_cert_number", "label": "ST Certificate Number", "type": "text", "required": True, "section": "Tribal Verification"},
            {"id": "category", "label": "Category", "type": "text", "required": True, "default": "ST", "read_only": True, "section": "Tribal Verification"},
            {"id": "is_pvtg", "label": "Belongs to PVTG?", "type": "select", "options": ["No", "Yes"], "required": True, "section": "Tribal Verification"},
            {"id": "target_country", "label": "Target Country of Study", "type": "select", "options": ["United Kingdom", "United States", "Germany", "Canada", "Australia", "Singapore"], "required": True, "section": "Overseas Study Details"},
            {"id": "foreign_university_name", "label": "Foreign University Name", "type": "text", "required": True, "section": "Overseas Study Details"},
            {"id": "course_abroad", "label": "Course / Degree Program Abroad", "type": "text", "required": True, "section": "Overseas Study Details"},
            {"id": "marks_percentage", "label": "Qualifying Degree Percentage (%)", "type": "number", "required": True, "section": "Academic Details"},
            {"id": "interview_appeared", "label": "Appeared in Expert Committee Interview?", "type": "select", "options": ["Yes", "No"], "required": True, "section": "Selection Details"},
            {"id": "interview_score", "label": "Expert Committee Interview Score (0-100)", "type": "number", "required": False, "section": "Selection Details"},
            {"id": "annual_income", "label": "Total Family Annual Income (INR ₹)", "type": "number", "required": True, "section": "Financial & Bank Info"},
            {"id": "bank_account_no", "label": "Bank Account Number", "type": "text", "required": True, "section": "Financial & Bank Info"},
            {"id": "bank_ifsc", "label": "Bank IFSC Code", "type": "text", "required": True, "section": "Financial & Bank Info"},
            {"id": "bank_name", "label": "Bank Name & Branch", "type": "text", "required": True, "section": "Financial & Bank Info"}
        ]
    )
    db.add(nos)

    # -------------------------------------------------------------------------
    # 4. SCHEME 3: TOP_CLASS (National Scholarship for Higher Education - Top Class)
    # Portal: https://scholarships.gov.in
    # Total Slots: 1000 slots/year | 246 Premier Institutes (IITs, IIMs, AIIMS, NITs)
    # -------------------------------------------------------------------------
    top_class = Scheme(
        code="TOP_CLASS",
        name="National Scholarship for Higher Education (Top Class)",
        full_title="National Fellowship and Scholarship for Higher Education of ST Students - Top Class Education Scheme",
        objective="To encourage meritorious ST students to pursue degree courses in 246 notified premier institutes of excellence across India.",
        financial_assistance="Full tuition fee reimbursement + living expense of ₹3,000/month + books & stationery ₹5,000/year + computer allowance ₹45,000 one-time.",
        target_group="ST Students admitted into 246 Notified Premier Institutes (IITs, IIMs, AIIMS, NITs, etc.)",
        income_ceiling=600000.0,
        min_marks=50.0,
        is_active=True,
        required_documents=[
            {
                "doc_type": "st_certificate",
                "title": "ST Caste Certificate",
                "description": "Valid caste certificate issued by Sub-Divisional Magistrate / Tehsildar.",
                "required": True,
                "target_fields": ["name", "caste", "certificate_number", "issuing_authority", "issue_date"]
            },
            {
                "doc_type": "income_certificate",
                "title": "Annual Income Certificate (<= ₹6.0L)",
                "description": "Income certificate for current financial year from competent revenue authority.",
                "required": True,
                "target_fields": ["name", "annual_income", "issuing_authority", "issue_date"]
            },
            {
                "doc_type": "marksheet_class12",
                "title": "Class XII Marksheet",
                "description": "Senior secondary / Class 12 board marksheet.",
                "required": True,
                "target_fields": ["name", "board", "percentage", "year"]
            },
            {
                "doc_type": "admission_letter",
                "title": "Admission Letter from Eligible Premier Institute",
                "description": "Confirmed admission letter from one of the 246 notified premier institutions.",
                "required": True,
                "target_fields": ["name", "institution", "course", "enrollment_date"]
            },
            {
                "doc_type": "bank_passbook",
                "title": "Bank Passbook First Page",
                "description": "Student's Aadhaar-linked savings bank account passbook copy.",
                "required": True,
                "target_fields": ["account_holder_name", "account_number", "ifsc_code", "bank_name"]
            },
            {
                "doc_type": "aadhaar_card",
                "title": "Aadhaar Card",
                "description": "UIDAI Aadhaar Card of the applicant.",
                "required": True,
                "target_fields": ["name", "dob", "aadhaar_number", "address"]
            }
        ],
        eligibility_rules={
            "scheme_id": "TOP_CLASS",
            "portal": "https://scholarships.gov.in",
            "category_required": "ST",
            "income_ceiling": 600000.0,
            "qualifying_exam": "Class XII",
            "min_qualifying_percentage": 50.0,
            "selection_mode": "Merit based on Class XII marks",
            "eligible_institution_types": ["IIT", "IIM", "AIIMS", "NIT", "IIIT", "Central University", "Other Premier Institute"],
            "notified_institutes_note": "Only 246 premier institutes eligible: IITs, AIIMs, IIMs, NITs, etc. Validate that institution_type is one of: IIT, IIM, AIIMS, NIT, IIIT, Central University, Other Premier Institute.",
            "preferred_groups": ["Girls", "Divyangjan", "PVTG"],
            "coverage": "Tuition fees, living expenses, books and computer allowance for entire course duration",
            "total_slots_per_year": 1000
        },
        merit_weights={
            "marks_weight": 0.80,
            "income_weight": 0.20,
            "female_bonus": 5.0,
            "pvtg_bonus": 5.0,
            "divyangjan_bonus": 3.0
        },
        form_fields=[
            {"id": "full_name", "label": "Full Name (as on ST Certificate)", "type": "text", "required": True, "section": "Personal Info"},
            {"id": "father_name", "label": "Father's / Guardian's Name", "type": "text", "required": True, "section": "Personal Info"},
            {"id": "gender", "label": "Gender", "type": "select", "options": ["Male", "Female", "Other"], "required": True, "section": "Personal Info"},
            {"id": "dob", "label": "Date of Birth", "type": "date", "required": True, "section": "Personal Info"},
            {"id": "phone", "label": "Mobile Number", "type": "tel", "required": True, "section": "Personal Info"},
            {"id": "state", "label": "Domicile State", "type": "select", "options": ALL_INDIAN_STATES_AND_UTS, "required": True, "section": "Tribal Verification"},
            {"id": "community_tribe", "label": "Sub-Caste / Tribe Name", "type": "text", "required": True, "section": "Tribal Verification"},
            {"id": "st_cert_number", "label": "ST Certificate Number", "type": "text", "required": True, "section": "Tribal Verification"},
            {"id": "category", "label": "Category", "type": "text", "required": True, "default": "ST", "read_only": True, "section": "Tribal Verification"},
            {"id": "is_pvtg", "label": "Belongs to PVTG?", "type": "select", "options": ["No", "Yes"], "required": True, "section": "Tribal Verification"},
            {"id": "is_divyangjan", "label": "Person with Benchmark Disability (Divyangjan)?", "type": "select", "options": ["No", "Yes"], "required": True, "section": "Personal Info"},
            {"id": "institution_type", "label": "Premier Institution Type", "type": "select", "options": ["IIT", "IIM", "AIIMS", "NIT", "IIIT", "Central University", "Other Premier Institute"], "required": True, "section": "Premier Academic Details"},
            {"id": "institution", "label": "Premier Institute Name", "type": "text", "required": True, "section": "Premier Academic Details"},
            {"id": "course", "label": "Degree / Course Name", "type": "text", "required": True, "section": "Premier Academic Details"},
            {"id": "marks_percentage", "label": "Class XII Marks (%)", "type": "number", "required": True, "section": "Premier Academic Details"},
            {"id": "annual_income", "label": "Annual Family Income (INR ₹)", "type": "number", "required": True, "section": "Financial & Bank Info"},
            {"id": "bank_account_no", "label": "Aadhaar-Linked Bank Account Number", "type": "text", "required": True, "section": "Financial & Bank Info"},
            {"id": "bank_ifsc", "label": "Bank IFSC Code", "type": "text", "required": True, "section": "Financial & Bank Info"},
            {"id": "bank_name", "label": "Bank Name & Branch", "type": "text", "required": True, "section": "Financial & Bank Info"}
        ]
    )
    db.add(top_class)

    # -------------------------------------------------------------------------
    # 5. SCHEME 4: POST_MATRIC (Post Matric Scholarship for ST Students)
    # Portal: https://dbttribal.gov.in/ | Implemented by States/UTs via NSP
    # Income Ceiling: Rs. 2,50,000/year | Universal Entitlement
    # -------------------------------------------------------------------------
    post_matric = Scheme(
        code="POST_MATRIC",
        name="Post Matric Scholarship for ST Students",
        full_title="Centrally Sponsored Post Matric Scholarship Scheme for Scheduled Tribe Students",
        objective="To provide financial support to Scheduled Tribe students studying at post-matriculation stages to complete their education.",
        financial_assistance="Compulsory institutional fee reimbursement + maintenance allowance of ₹230 to ₹1,200/month as per course category.",
        target_group="ST Students in Post-Matric Courses (Class XI onwards, Degrees, Diplomas)",
        income_ceiling=250000.0,
        min_marks=35.0,
        is_active=True,
        required_documents=[
            {
                "doc_type": "st_certificate",
                "title": "ST Caste Certificate",
                "description": "Valid caste certificate issued by Tehsildar / SDO.",
                "required": True,
                "target_fields": ["name", "caste", "certificate_number", "issuing_authority", "issue_date"]
            },
            {
                "doc_type": "income_certificate",
                "title": "Income Certificate (Ceiling: ₹2,50,000)",
                "description": "Certificate certifying annual family income does not exceed ₹2,50,000.",
                "required": True,
                "target_fields": ["name", "annual_income", "issuing_authority", "issue_date"]
            },
            {
                "doc_type": "marksheet_class10",
                "title": "Class X (Matriculation) Marksheet",
                "description": "Proof of passing Class X matriculation examination.",
                "required": True,
                "target_fields": ["name", "board", "percentage", "year"]
            },
            {
                "doc_type": "admission_letter",
                "title": "Current Course Admission / Enrollment Proof",
                "description": "Bonafide admission certificate or enrollment receipt for current session.",
                "required": True,
                "target_fields": ["name", "institution", "course", "enrollment_date"]
            },
            {
                "doc_type": "bank_passbook",
                "title": "Bank Passbook First Page",
                "description": "Aadhaar-seeded bank account details for DBT credit.",
                "required": True,
                "target_fields": ["account_holder_name", "account_number", "ifsc_code", "bank_name"]
            },
            {
                "doc_type": "aadhaar_card",
                "title": "Aadhaar Card",
                "description": "Applicant's official Aadhaar card.",
                "required": True,
                "target_fields": ["name", "dob", "aadhaar_number", "address"]
            },
            {
                "doc_type": "fee_receipt",
                "title": "Institution Fee Receipt",
                "description": "Official receipt of compulsory non-refundable fees paid for reimbursement component.",
                "required": True,
                "target_fields": ["institution", "receipt_number", "amount", "date"]
            }
        ],
        eligibility_rules={
            "scheme_id": "POST_MATRIC",
            "portal": "https://dbttribal.gov.in/",
            "category_required": "ST",
            "income_ceiling": 250000.0,
            "qualifying_exam": "Matriculation / Class X Passed",
            "min_qualifying_percentage": 35.0,
            "eligible_courses": ["Any recognized post-matric course from recognized institution"],
            "funding_ratio": "75:25 Centre:State (90:10 for NE & Himalayan States; 100% UTs without legislature)",
            "implemented_by": "States/UTs via National Scholarship Portal"
        },
        merit_weights={
            "marks_weight": 0.70,
            "income_weight": 0.30,
            "female_bonus": 5.0,
            "pvtg_bonus": 5.0
        },
        form_fields=[
            {"id": "full_name", "label": "Full Name (as on ST Certificate)", "type": "text", "required": True, "section": "Personal Info"},
            {"id": "father_name", "label": "Father's / Guardian's Name", "type": "text", "required": True, "section": "Personal Info"},
            {"id": "gender", "label": "Gender", "type": "select", "options": ["Male", "Female", "Other"], "required": True, "section": "Personal Info"},
            {"id": "dob", "label": "Date of Birth", "type": "date", "required": True, "section": "Personal Info"},
            {"id": "phone", "label": "Mobile Number", "type": "tel", "required": True, "section": "Personal Info"},
            {"id": "state", "label": "Domicile State", "type": "select", "options": ALL_INDIAN_STATES_AND_UTS, "required": True, "section": "Tribal Verification"},
            {"id": "community_tribe", "label": "Sub-Caste / Tribe Name", "type": "text", "required": True, "section": "Tribal Verification"},
            {"id": "st_cert_number", "label": "ST Certificate Number", "type": "text", "required": True, "section": "Tribal Verification"},
            {"id": "category", "label": "Category", "type": "text", "required": True, "default": "ST", "read_only": True, "section": "Tribal Verification"},
            {"id": "is_pvtg", "label": "Belongs to PVTG?", "type": "select", "options": ["No", "Yes"], "required": True, "section": "Tribal Verification"},
            {"id": "institution", "label": "College / University / Polytech Name", "type": "text", "required": True, "section": "Academic Details"},
            {"id": "course", "label": "Course of Study", "type": "text", "required": True, "section": "Academic Details"},
            {"id": "marks_percentage", "label": "Class X / Last Exam Percentage (%)", "type": "number", "required": True, "section": "Academic Details"},
            {"id": "annual_income", "label": "Annual Family Income (Ceiling: ₹2,50,000)", "type": "number", "required": True, "section": "Financial & Bank Info"},
            {"id": "bank_account_no", "label": "Bank Account Number", "type": "text", "required": True, "section": "Financial & Bank Info"},
            {"id": "bank_ifsc", "label": "Bank IFSC Code", "type": "text", "required": True, "section": "Financial & Bank Info"},
            {"id": "bank_name", "label": "Bank Name & Branch", "type": "text", "required": True, "section": "Financial & Bank Info"}
        ]
    )
    db.add(post_matric)

    # -------------------------------------------------------------------------
    # 6. SCHEME 5: PRE_MATRIC (Pre Matric Scholarship for ST Students)
    # Portal: https://dbttribal.gov.in/ | Implemented by States/UTs via NSP
    # Class: IX & X only | Income Ceiling: Rs. 2,50,000/year
    # -------------------------------------------------------------------------
    pre_matric = Scheme(
        code="PRE_MATRIC",
        name="Pre Matric Scholarship for ST Students",
        full_title="Centrally Sponsored Scheme of Pre-Matric Scholarship for Needy ST Students (Classes IX & X)",
        objective="To support parents of ST children for education of their wards studying in classes IX and X to minimize dropout rates.",
        financial_assistance="Day scholars: ₹225/month for 10 months (₹2,250/year); Hostellers: ₹525/month for 10 months (₹5,250/year) plus book grants.",
        target_group="Needy ST Students in Classes IX & X in recognized schools",
        income_ceiling=250000.0,
        min_marks=33.0,
        is_active=True,
        required_documents=[
            {
                "doc_type": "st_certificate",
                "title": "ST Caste Certificate",
                "description": "Valid caste certificate issued by competent authority.",
                "required": True,
                "target_fields": ["name", "caste", "certificate_number", "issuing_authority", "issue_date"]
            },
            {
                "doc_type": "income_certificate",
                "title": "Annual Income Certificate (Ceiling: ₹2,50,000)",
                "description": "Certificate proving family income does not exceed ₹2,50,000.",
                "required": True,
                "target_fields": ["name", "annual_income", "issuing_authority", "issue_date"]
            },
            {
                "doc_type": "school_bonafide",
                "title": "School Enrollment / Bonafide Certificate",
                "description": "Bonafide student certificate issued by School Headmaster / Principal.",
                "required": True,
                "target_fields": ["name", "class", "school", "year"]
            },
            {
                "doc_type": "marksheet_previous",
                "title": "Previous Year Marksheet (Class VIII / IX)",
                "description": "Marksheet of the previous academic standard passed.",
                "required": True,
                "target_fields": ["name", "class", "percentage", "year"]
            },
            {
                "doc_type": "bank_passbook",
                "title": "Bank Passbook (Parent / Student Account)",
                "description": "Savings account passbook (can be parent's account if student is minor).",
                "required": True,
                "target_fields": ["account_holder_name", "account_number", "ifsc_code", "bank_name"]
            },
            {
                "doc_type": "aadhaar_card",
                "title": "Aadhaar Card (Student & Parent)",
                "description": "Aadhaar identity proof.",
                "required": True,
                "target_fields": ["name", "dob", "aadhaar_number", "address"]
            },
            {
                "doc_type": "hostel_certificate",
                "title": "Hostel Certificate (if Hosteller)",
                "description": "Certificate from recognized hostel warden if claiming hosteller rate.",
                "required": False,
                "target_fields": ["student_name", "hostel_name", "warden_signature", "date"]
            }
        ],
        eligibility_rules={
            "scheme_id": "PRE_MATRIC",
            "portal": "https://dbttribal.gov.in/",
            "category_required": "ST",
            "income_ceiling": 250000.0,
            "eligible_classes": ["Class IX", "Class X", "IX", "X"],
            "student_types": ["Day Scholar", "Hosteller"],
            "funding_ratio": "75:25 Centre:State (90:10 for NE & Himalayan States; 100% UTs without legislature)",
            "implemented_by": "States/UTs via National Scholarship Portal"
        },
        merit_weights={
            "marks_weight": 0.60,
            "income_weight": 0.40,
            "female_bonus": 5.0,
            "pvtg_bonus": 5.0
        },
        form_fields=[
            {"id": "full_name", "label": "Student Full Name", "type": "text", "required": True, "section": "Personal Info"},
            {"id": "father_name", "label": "Father's / Parent's Name", "type": "text", "required": True, "section": "Personal Info"},
            {"id": "gender", "label": "Gender", "type": "select", "options": ["Male", "Female", "Other"], "required": True, "section": "Personal Info"},
            {"id": "dob", "label": "Date of Birth", "type": "date", "required": True, "section": "Personal Info"},
            {"id": "phone", "label": "Parent's Mobile Number", "type": "tel", "required": True, "section": "Personal Info"},
            {"id": "state", "label": "Domicile State", "type": "select", "options": ALL_INDIAN_STATES_AND_UTS, "required": True, "section": "Tribal Verification"},
            {"id": "community_tribe", "label": "Sub-Caste / Tribe Name", "type": "text", "required": True, "section": "Tribal Verification"},
            {"id": "st_cert_number", "label": "ST Certificate Number", "type": "text", "required": True, "section": "Tribal Verification"},
            {"id": "category", "label": "Category", "type": "text", "required": True, "default": "ST", "read_only": True, "section": "Tribal Verification"},
            {"id": "is_pvtg", "label": "Belongs to PVTG?", "type": "select", "options": ["No", "Yes"], "required": True, "section": "Tribal Verification"},
            {"id": "institution", "label": "School Name & Address", "type": "text", "required": True, "section": "School Details"},
            {"id": "course", "label": "Class Enrolled", "type": "select", "options": ["Class IX", "Class X"], "required": True, "section": "School Details"},
            {"id": "student_type", "label": "Student Residence Type", "type": "select", "options": ["Day Scholar", "Hosteller"], "required": True, "section": "School Details"},
            {"id": "marks_percentage", "label": "Previous Standard Marks (%)", "type": "number", "required": True, "section": "School Details"},
            {"id": "annual_income", "label": "Annual Family Income (Ceiling: ₹2,50,000)", "type": "number", "required": True, "section": "Financial & Bank Info"},
            {"id": "bank_account_no", "label": "Bank Account Number (Parent/Minor)", "type": "text", "required": True, "section": "Financial & Bank Info"},
            {"id": "bank_ifsc", "label": "Bank IFSC Code", "type": "text", "required": True, "section": "Financial & Bank Info"},
            {"id": "bank_name", "label": "Bank Name & Branch", "type": "text", "required": True, "section": "Financial & Bank Info"}
        ]
    )
    db.add(pre_matric)
    db.flush()

    # -------------------------------------------------------------------------
    # 7. 18 SEEDED APPLICANTS DISTRIBUTED ACROSS ALL 5 SCHEMES
    # Distribution: 5 NFST, 3 NOS, 4 TOP_CLASS, 3 POST_MATRIC, 3 PRE_MATRIC = 18
    # Using authentic Indian ST communities: Santhal, Gond, Bhil, Munda, Khasi,
    # Bodo, Ho, Oraon, Chenchu (PVTG), Toda (PVTG).
    # Includes all deliberate test cases:
    # - 2 sharing ST cert (collision fraud)
    # - 1 wrong slot upload (classifier warning)
    # - 1 blurry/tampered document (forensic signal)
    # - 2 DigiLocker-verified applicants (green fast-track)
    # -------------------------------------------------------------------------
    candidates_data = [
        # --- NFST (5 Candidates) ---
        # 1. Genuine Selected Scholar (Jharkhand, Santhal)
        {
            "name": "Birsa Soren",
            "email": "birsa.soren@research.ac.in",
            "state": "Jharkhand",
            "tribe": "Santhal",
            "st_cert": "ST/JH/2023/1029",
            "scheme": nfst,
            "course": "Ph.D",
            "inst": "Central University of Jharkhand",
            "marks": 78.5,
            "income": 240000.0,
            "status": "Selected",
            "disb_status": "Active Fellowship Disbursement",
            "disb_amount": 432000.0,
            "bank_account": "308940029001",
            "dob": "1998-05-12",
            "gender": "Male",
            "is_pvtg": False,
            "discrepancy": False,
            "file_hash_st": "a1b2c3d4e5f60718293a4b5c6d7e8f90123456789abcdef0123456789abcdef0"
        },
        # 2. FRAUD ENGINE COLLISION DEMO (Collides with Birsa Soren: Duplicate ST Cert + Bank + DOB + File Hash)
        {
            "name": "Birsa M. Soren",
            "email": "somra.soren@research.in",
            "state": "Jharkhand",
            "tribe": "Santhal",
            "st_cert": "ST/JH/2023/1029",  # COLLISION WITH BIRSA SOREN!
            "scheme": nfst,
            "course": "Ph.D",
            "inst": "Ranchi University",
            "marks": 71.0,
            "income": 250000.0,
            "status": "Needs Review",
            "disb_status": "Flagged by Fraud Engine",
            "disb_amount": 0.0,
            "bank_account": "308940029001",  # DUPLICATE BANK ACCOUNT!
            "dob": "1998-05-12",  # IDENTICAL DOB!
            "gender": "Male",
            "is_pvtg": False,
            "discrepancy": True,
            "deficiency_doc": "st_certificate",
            "deficiency_reason": "High fraud risk: ST Certificate number ST/JH/2023/1029 and DBT bank account are already registered in active application NFST-2026-1001.",
            "file_hash_st": "a1b2c3d4e5f60718293a4b5c6d7e8f90123456789abcdef0123456789abcdef0"
        },
        # 3. DIGILOCKER FAST-TRACK DEMO 1 (Munda Tribe, Jharkhand - 100% verified)
        {
            "name": "Birsa Munda",
            "email": "birsa.munda@tribal-edu.in",
            "state": "Jharkhand",
            "tribe": "Munda",
            "st_cert": "ST/JH/2024/9912",
            "scheme": nfst,
            "course": "Ph.D",
            "inst": "Birsa Agricultural University",
            "marks": 84.5,
            "income": 180000.0,
            "status": "Selected",
            "disb_status": "Active Fellowship Disbursement",
            "disb_amount": 432000.0,
            "bank_account": "308940029003",
            "dob": "1997-11-15",
            "gender": "Male",
            "is_pvtg": False,
            "is_digilocker": True,
            "is_aadhaar": True,
            "discrepancy": False
        },
        # 4. DIGILOCKER FAST-TRACK DEMO 2 (Santhal Tribe, Odisha - Female Scholar)
        {
            "name": "Sunita Soren",
            "email": "sunita.soren@tribal-edu.in",
            "state": "Odisha",
            "tribe": "Santhal",
            "st_cert": "ST/OD/2024/8801",
            "scheme": nfst,
            "course": "Ph.D",
            "inst": "Utkal University",
            "marks": 81.0,
            "income": 220000.0,
            "status": "Scrutiny",
            "disb_status": "Pending Committee Sanction",
            "disb_amount": 0.0,
            "bank_account": "308940029004",
            "dob": "1999-03-22",
            "gender": "Female",
            "is_pvtg": False,
            "is_digilocker": True,
            "is_aadhaar": True,
            "discrepancy": False
        },
        # 5. WRONG-SLOT CLASSIFIER DEMO (Admission letter in Income Certificate slot)
        {
            "name": "Pooja Halba",
            "email": "pooja.halba@stmail.in",
            "state": "Chhattisgarh",
            "tribe": "Halba",
            "st_cert": "ST/CG/2024/9931",
            "scheme": nfst,
            "course": "Ph.D",
            "inst": "Pandit Ravishankar Shukla University",
            "marks": 68.0,
            "income": 250000.0,
            "status": "Needs Review",
            "disb_status": "Deficiency Action Required",
            "disb_amount": 0.0,
            "bank_account": "308940029005",
            "dob": "2000-08-19",
            "gender": "Female",
            "is_pvtg": False,
            "discrepancy": True,
            "wrong_slot_demo": True,
            "deficiency_doc": "income_certificate",
            "deficiency_reason": "Slot Mismatch: Uploaded document in Income Certificate slot is identified by AI as an Admission Offer Letter. Please upload valid Income Certificate."
        },

        # --- NOS (3 Candidates) ---
        # 6. Oxford Overseas Scholar (Munda Tribe, Odisha)
        {
            "name": "Rupesh Munda",
            "email": "rupesh.munda@oxford.edu",
            "state": "Odisha",
            "tribe": "Munda",
            "st_cert": "ST/OD/2023/4521",
            "scheme": nos,
            "course": "Master's",
            "inst": "University of Oxford",
            "target_country": "United Kingdom",
            "marks": 85.4,
            "income": 360000.0,
            "status": "Selected",
            "disb_status": "Tuition & Allowance Sanctioned",
            "disb_amount": 1850000.0,
            "bank_account": "308940029006",
            "dob": "1996-07-28",
            "gender": "Male",
            "is_pvtg": False,
            "interview_score": 88.0,
            "discrepancy": False
        },
        # 7. University of Edinburgh (Khasi Tribe, Meghalaya - Female Scholar)
        {
            "name": "Grace Nongrum",
            "email": "grace.nongrum@ed.ac.uk",
            "state": "Meghalaya",
            "tribe": "Khasi",
            "st_cert": "ST/ML/2023/9014",
            "scheme": nos,
            "course": "Ph.D",
            "inst": "University of Edinburgh",
            "target_country": "United Kingdom",
            "marks": 76.8,
            "income": 420000.0,
            "status": "Scrutiny",
            "disb_status": "Pending Committee Sanction",
            "disb_amount": 0.0,
            "bank_account": "308940029007",
            "dob": "1998-12-10",
            "gender": "Female",
            "is_pvtg": False,
            "interview_score": 82.0,
            "discrepancy": False
        },
        # 8. University of Manchester Deficiency Case (Angami Tribe, Nagaland)
        {
            "name": "Nehemiah Angami",
            "email": "nehemiah.angami@manchester.ac.uk",
            "state": "Nagaland",
            "tribe": "Angami",
            "st_cert": "ST/NL/2023/7611",
            "scheme": nos,
            "course": "Master's",
            "inst": "University of Manchester",
            "target_country": "United Kingdom",
            "marks": 72.0,
            "income": 490000.0,
            "status": "Needs Review",
            "disb_status": "Deficiency Action Required",
            "disb_amount": 0.0,
            "bank_account": "308940029008",
            "dob": "1998-06-30",
            "gender": "Male",
            "is_pvtg": False,
            "interview_score": 75.0,
            "discrepancy": True,
            "deficiency_doc": "admission_letter",
            "deficiency_reason": "Conditional admission offer uploaded. MoTA NOS guidelines mandate unconditional offer letter."
        },

        # --- TOP_CLASS (4 Candidates) ---
        # 9. IIT Bombay Selected Scholar (Gond Tribe, MP - Female)
        {
            "name": "Anjali Gond",
            "email": "anjali.gond@iitb.ac.in",
            "state": "Madhya Pradesh",
            "tribe": "Gond",
            "st_cert": "ST/MP/2024/2281",
            "scheme": top_class,
            "course": "B.Tech in Computer Science",
            "inst": "Indian Institute of Technology Bombay",
            "inst_type": "IIT",
            "marks": 91.5,
            "income": 280000.0,
            "status": "Selected",
            "disb_status": "Tuition & Living Allowance Active",
            "disb_amount": 285000.0,
            "bank_account": "308940029009",
            "dob": "2006-04-12",
            "gender": "Female",
            "is_pvtg": False,
            "discrepancy": False
        },
        # 10. AIIMS New Delhi PVTG Candidate (Chenchu Tribe, Andhra Pradesh)
        {
            "name": "Kameshwar Chenchu",
            "email": "kameshwar.chenchu@aiims.edu",
            "state": "Andhra Pradesh",
            "tribe": "Chenchu (PVTG)",
            "st_cert": "ST/AP/2024/1105",
            "scheme": top_class,
            "course": "MBBS",
            "inst": "All India Institute of Medical Sciences New Delhi",
            "inst_type": "AIIMS",
            "marks": 89.0,
            "income": 150000.0,
            "status": "Scrutiny",
            "disb_status": "In Scrutiny Queue",
            "disb_amount": 0.0,
            "bank_account": "308940029010",
            "dob": "2005-09-18",
            "gender": "Male",
            "is_pvtg": True,  # PVTG BONUS APPLICABLE
            "discrepancy": False
        },
        # 11. FORENSIC TAMPERING & BLUR DEMO (Warli Tribe, Maharashtra - NIT Nagpur)
        {
            "name": "Priyanka Warli",
            "email": "priyanka.warli@mu.ac.in",
            "state": "Maharashtra",
            "tribe": "Warli",
            "st_cert": "ST/MH/2023/4192",
            "scheme": top_class,
            "course": "B.Tech in Civil Engineering",
            "inst": "Visvesvaraya National Institute of Technology Nagpur",
            "inst_type": "NIT",
            "marks": 74.0,
            "income": 290000.0,
            "status": "Needs Review",
            "disb_status": "Deficiency Action Required",
            "disb_amount": 0.0,
            "bank_account": "308940029011",
            "dob": "2006-01-14",
            "gender": "Female",
            "is_pvtg": False,
            "discrepancy": True,
            "tamper_demo": True,
            "deficiency_doc": "st_certificate",
            "deficiency_reason": "Authenticity Advisory: Document exhibits high blur (Laplacian variance 38.2), screen photography moiré patterns, and Adobe Photoshop editing metadata. Clear original scan required."
        },
        # 12. IIM Ahmedabad Scholar (Bhil Tribe, Rajasthan)
        {
            "name": "Vikram Bhil",
            "email": "vikram.bhil@iima.ac.in",
            "state": "Rajasthan",
            "tribe": "Bhil",
            "st_cert": "ST/RJ/2024/7702",
            "scheme": top_class,
            "course": "Integrated MBA",
            "inst": "Indian Institute of Management Ahmedabad",
            "inst_type": "IIM",
            "marks": 86.5,
            "income": 340000.0,
            "status": "Under Verification",
            "disb_status": "Queued for Verification",
            "disb_amount": 0.0,
            "bank_account": "308940029012",
            "dob": "2005-11-20",
            "gender": "Male",
            "is_pvtg": False,
            "discrepancy": False
        },

        # --- POST_MATRIC (3 Candidates) ---
        # 13. Gauhati University Post-Matric Scholar (Bodo Tribe, Assam - Female)
        {
            "name": "Kavita Bodo",
            "email": "kavita.bodo@gu.ac.in",
            "state": "Assam",
            "tribe": "Bodo",
            "st_cert": "ST/AS/2024/5512",
            "scheme": post_matric,
            "course": "B.Sc. in Botany",
            "inst": "Gauhati University",
            "marks": 78.0,
            "income": 180000.0,
            "status": "Selected",
            "disb_status": "State DBT Disbursed (75:25 Sharing)",
            "disb_amount": 24000.0,
            "bank_account": "308940029013",
            "dob": "2004-03-15",
            "gender": "Female",
            "is_pvtg": False,
            "discrepancy": False
        },
        # 14. Govt Polytechnic Diploma (Ho Tribe, Jharkhand)
        {
            "name": "Somra Ho",
            "email": "somra.ho@polytech.ac.in",
            "state": "Jharkhand",
            "tribe": "Ho",
            "st_cert": "ST/JH/2024/4390",
            "scheme": post_matric,
            "course": "Diploma in Mechanical Engineering",
            "inst": "Government Polytechnic Ranchi",
            "marks": 72.0,
            "income": 140000.0,
            "status": "Under Verification",
            "disb_status": "In Scrutiny Queue",
            "disb_amount": 0.0,
            "bank_account": "308940029014",
            "dob": "2005-07-22",
            "gender": "Male",
            "is_pvtg": False,
            "discrepancy": False
        },
        # 15. Ineligible Income Breach (Gond Tribe, Maharashtra - ₹3.8L exceeds ₹2.5L limit)
        {
            "name": "Deepak Naik",
            "email": "deepak.naik@stmail.in",
            "state": "Maharashtra",
            "tribe": "Gond",
            "st_cert": "ST/MH/2024/9021",
            "scheme": post_matric,
            "course": "B.Com",
            "inst": "Savitribai Phule Pune University",
            "marks": 64.0,
            "income": 380000.0,  # BREACHES POST MATRIC ₹2.5L CEILING
            "status": "Rejected",
            "disb_status": "Ineligible",
            "disb_amount": 0.0,
            "bank_account": "308940029015",
            "dob": "2003-10-05",
            "gender": "Male",
            "is_pvtg": False,
            "discrepancy": True,
            "deficiency_doc": "income_certificate",
            "deficiency_reason": "Statutory Income Ceiling Breached: Declared family income ₹3,80,000 exceeds Post-Matric ceiling limit of ₹2,50,000."
        },

        # --- PRE_MATRIC (3 Candidates) ---
        # 16. Netarhat Residential School Hosteller (Oraon Tribe, Jharkhand)
        {
            "name": "Mangal Oraon",
            "email": "mangal.oraon@netarhat.edu",
            "state": "Jharkhand",
            "tribe": "Oraon",
            "st_cert": "ST/JH/2024/6610",
            "scheme": pre_matric,
            "course": "Class X",
            "inst": "Netarhat Residential School",
            "student_type": "Hosteller",
            "marks": 74.0,
            "income": 120000.0,
            "status": "Selected",
            "disb_status": "Hosteller Allowance Sanctioned",
            "disb_amount": 5250.0,
            "bank_account": "308940029016",
            "dob": "2009-08-11",
            "gender": "Male",
            "is_pvtg": False,
            "discrepancy": False
        },
        # 17. Nilgiris Tribal Govt School PVTG Scholar (Toda Tribe, Tamil Nadu - Female)
        {
            "name": "Malini Toda",
            "email": "malini.toda@tnedu.in",
            "state": "Tamil Nadu",
            "tribe": "Toda (PVTG)",
            "st_cert": "ST/TN/2024/3301",
            "scheme": pre_matric,
            "course": "Class IX",
            "inst": "Nilgiris Tribal Government High School",
            "student_type": "Day Scholar",
            "marks": 76.5,
            "income": 95000.0,
            "status": "Under Verification",
            "disb_status": "In Scrutiny Queue",
            "disb_amount": 0.0,
            "bank_account": "308940029017",
            "dob": "2010-02-14",
            "gender": "Female",
            "is_pvtg": True,  # PVTG BONUS APPLICABLE
            "discrepancy": False
        },
        # 18. Ineligible Pre-Matric Income Breach (Bhil Tribe, MP - ₹2.9L exceeds ₹2.5L limit)
        {
            "name": "Rohan Kumar",
            "email": "rohan.kumar@mpedu.in",
            "state": "Madhya Pradesh",
            "tribe": "Bhil",
            "st_cert": "ST/MP/2024/8812",
            "scheme": pre_matric,
            "course": "Class IX",
            "inst": "Government Model School Jhabua",
            "student_type": "Day Scholar",
            "marks": 51.5,
            "income": 290000.0,  # BREACHES PRE MATRIC ₹2.5L CEILING
            "status": "Rejected",
            "disb_status": "Ineligible",
            "disb_amount": 0.0,
            "bank_account": "308940029018",
            "dob": "2010-06-25",
            "gender": "Male",
            "is_pvtg": False,
            "discrepancy": True,
            "deficiency_doc": "income_certificate",
            "deficiency_reason": "Statutory Income Ceiling Breached: Family income ₹2,90,000 exceeds Pre-Matric ceiling limit of ₹2,50,000."
        }
    ]

    created_apps = []

    for idx, c in enumerate(candidates_data, 1):
        user = User(
            email=c["email"],
            hashed_password=get_password_hash("scholar123"),
            role="applicant",
            full_name=c["name"],
            st_cert_number=c["st_cert"],
            phone=f"+91-98765-{idx:04d}",
            state=c["state"],
            community_tribe=c["tribe"],
            institution=c["inst"],
            course=c["course"],
            created_at=datetime.utcnow() - timedelta(days=idx * 2)
        )
        db.add(user)
        db.flush()

        app_num = f"{c['scheme'].code}-2026-{idx + 1000:04d}"
        form_data = {
            "full_name": c["name"],
            "father_name": f"{c['name'].split()[0]}'s Guardian",
            "gender": c.get("gender", "Male"),
            "dob": c.get("dob", "1998-05-12"),
            "phone": user.phone,
            "state": c["state"],
            "community_tribe": c["tribe"],
            "st_cert_number": c["st_cert"],
            "category": "ST",
            "is_pvtg": "Yes" if c.get("is_pvtg") else "No",
            "course": c["course"],
            "degree_level": c["course"],
            "institution": c["inst"],
            "institution_type": c.get("inst_type", "Central University"),
            "target_country": c.get("target_country"),
            "foreign_university_name": c["inst"] if c["scheme"].code == "NOS" else None,
            "student_type": c.get("student_type", "Day Scholar"),
            "research_topic": f"Field Study on Tribal Socio-Economic Empowerment in {c['state']}",
            "marks_percentage": c["marks"],
            "interview_score": c.get("interview_score"),
            "annual_income": c["income"],
            "bank_account_no": c.get("bank_account", f"308940029{idx:03d}"),
            "bank_ifsc": "SBIN0001234",
            "bank_name": "State Bank of India",
            "passport_no": f"T{892010 + idx}" if c["scheme"].code == "NOS" else None
        }

        is_eligible, notes, breakdown = evaluate_eligibility(c["scheme"].eligibility_rules, form_data)
        merit_score = calculate_merit_score(
            form_data,
            income_ceiling=c["scheme"].income_ceiling,
            merit_weights=c["scheme"].merit_weights
        )

        application = Application(
            application_number=app_num,
            user_id=user.id,
            scheme_id=c["scheme"].id,
            status=c["status"],
            form_data=form_data,
            eligibility_passed=is_eligible,
            eligibility_notes=notes,
            calculated_merit_score=merit_score,
            disbursement_status=c["disb_status"],
            disbursement_amount=c["disb_amount"],
            renewal_due_date="2027-03-31" if c["status"] == "Selected" else None,
            is_digilocker_verified=bool(c.get("is_digilocker")),
            is_aadhaar_verified=bool(c.get("is_aadhaar")),
            aadhaar_data={
                "aadhaar_last4": f"89{idx:02d}",
                "name": c["name"],
                "verified": True,
                "state": c["state"]
            } if c.get("is_aadhaar") else {},
            submission_date=datetime.utcnow() - timedelta(days=idx * 2),
            created_at=datetime.utcnow() - timedelta(days=idx * 2)
        )
        db.add(application)
        db.flush()
        created_apps.append((application, c))

        # Attach documents matching scheme requirements
        req_docs = c["scheme"].required_documents or []
        for d_def in req_docs:
            dtype = d_def["doc_type"]
            fname = f"{dtype}_{app_num.lower()}.pdf"
            fpath = f"/uploads/{fname}"

            extracted = {}
            if dtype == "st_certificate":
                extracted = parse_st_certificate(f"Certificate No: {c['st_cert']}\nName: {c['name']}\nTribe: {c['tribe']}", form_data)
            elif dtype == "income_certificate":
                extracted = parse_income_certificate(f"Income certificate certifying Rs. {c['income']:.0f} per annum", form_data)
            elif dtype == "admission_letter":
                extracted = parse_admission_letter(f"Admission to {c['inst']}", form_data)
            elif dtype.startswith("marksheet"):
                extracted = parse_marksheet(f"Aggregate marks: {c['marks']}%", form_data)
            elif dtype == "passport":
                extracted = {"passport_number": f"T{892010 + idx}", "name": c["name"], "nationality": "Indian"}
            elif dtype == "bank_passbook":
                extracted = {"account_holder_name": c["name"], "account_number": c.get("bank_account"), "ifsc_code": "SBIN0001234", "bank_name": "State Bank of India"}
            elif dtype == "aadhaar_card":
                extracted = {"name": c["name"], "dob": c.get("dob", "1998-05-12"), "aadhaar_number": f"XXXX-XXXX-89{idx:02d}"}
            else:
                extracted = {"valid": True, "type": dtype, "candidate_name": c["name"]}

            doc_status, conf, comp_res = cross_verify_document(dtype, extracted, form_data)
            predicted_type = dtype
            classifier_conf = 0.95
            type_mismatch = False
            tampering_signals = {
                "overall_authenticity": "Authentic (Verified)",
                "blur_detected": False,
                "laplacian_variance": 284.5,
                "moire_screen_photo": False,
                "tamper_flags": [],
                "recommendation": "Advisory: Document passes standard clarity and structural checks."
            }

            # Handle wrong-slot demo
            if c.get("wrong_slot_demo") and dtype == "income_certificate":
                predicted_type = "admission_letter"
                classifier_conf = 0.94
                type_mismatch = True
                doc_status = "Needs Review"
                conf = 48.0
                extracted = {
                    "institution_name": "Pandit Ravishankar Shukla University",
                    "course_name": "Ph.D. in Social Sciences",
                    "academic_session": "2024-25"
                }
                comp_res = {
                    "annual_income": {"matched": False, "form_value": 250000.0, "doc_value": None, "warning": "No income figure found in admission letter"},
                    "slot_mismatch": True,
                    "warning": "Wrong-slot document: AI Classifier detected Ph.D Admission Offer Letter instead of Income Certificate."
                }

            # Handle tampering demo
            if c.get("tamper_demo") and dtype == "st_certificate":
                doc_status = "Needs Review"
                conf = 52.0
                tampering_signals = {
                    "laplacian_variance": 38.2,
                    "blur_detected": True,
                    "blur_severity": "High Blur (Unreadable Fine Print/Stamp)",
                    "moire_screen_photo": True,
                    "tamper_flags": ["Software: Adobe Photoshop 2023 (EXIF metadata indicates image manipulation)"],
                    "dimensions": {"width": 640, "height": 480},
                    "is_low_res": True,
                    "overall_authenticity": "Suspicious (Image Editing Suite Detected)",
                    "recommendation": "Advisory signal for human review: Blurry fine print, screen photography moiré patterns, and image editing metadata detected. Verify original physical caste certificate."
                }

            # Handle DigiLocker verified docs
            if c.get("is_digilocker"):
                doc_status = "Verified"
                conf = 100.0
                tampering_signals = {
                    "overall_authenticity": "Authentic (Cryptographically Signed)",
                    "blur_detected": False,
                    "laplacian_variance": 450.0,
                    "moire_screen_photo": False,
                    "tamper_flags": [],
                    "recommendation": "Document cryptographically issued and verified via DigiLocker National Locker Service (100% confidence)."
                }

            file_hash = c.get("file_hash_st") if dtype == "st_certificate" and c.get("file_hash_st") else hashlib.sha256(f"{app_num}_{dtype}".encode()).hexdigest()

            doc = Document(
                application_id=application.id,
                doc_type=dtype,
                file_name=fname,
                file_path=fpath,
                file_size=245000 + (idx * 15000),
                file_hash=file_hash,
                status=doc_status,
                confidence_score=conf,
                extracted_data=extracted,
                comparison_data=comp_res,
                predicted_type=predicted_type,
                classifier_confidence=classifier_conf,
                type_mismatch=type_mismatch,
                tampering_signals=tampering_signals,
                is_digilocker_issued=bool(c.get("is_digilocker")),
                digilocker_uri=f"in.gov.edistrict.{dtype}.2024.{idx:05d}" if c.get("is_digilocker") else None,
                ocr_text=f"MoTA Scrutiny Intelligence Engine\nDocument: {d_def['title']}\nStatus: {doc_status}\nHash: {file_hash[:16]}...",
                upload_date=datetime.utcnow() - timedelta(days=idx * 2)
            )
            db.add(doc)
            db.flush()

            if c.get("discrepancy") and c.get("deficiency_doc") == dtype:
                defic = Deficiency(
                    application_id=application.id,
                    document_id=doc.id,
                    doc_type=dtype,
                    flagged_by="MoTA Scrutiny Officer",
                    reason=c.get("deficiency_reason", "Discrepancy flagged during automated verification."),
                    status="Open",
                    created_at=datetime.utcnow() - timedelta(days=1)
                )
                db.add(defic)

        # Standard Activity Timeline Logs
        db.add(ActivityLog(
            application_id=application.id,
            action="Application Submitted",
            actor=c["name"],
            stage="Submitted",
            remarks=f"Application {app_num} submitted successfully via MoTA Single Window Portal.",
            created_at=datetime.utcnow() - timedelta(days=idx * 2)
        ))
        db.add(ActivityLog(
            application_id=application.id,
            action="AI Document Verification Processed",
            actor="MoTA AI-OCR Engine",
            stage="Under Verification",
            remarks="Automated field cross-matching, slot classification, and tampering check completed.",
            created_at=datetime.utcnow() - timedelta(days=idx * 2, hours=-1)
        ))

        # ---------------------------------------------------------------------
        # 8. CRYPTOGRAPHIC AUDIT LEDGER (SHA-256 Chained Blocks)
        # ---------------------------------------------------------------------
        # Block 1: Application Submission
        log_action(
            db=db,
            application_id=application.id,
            actor_name=c["name"],
            actor_role="applicant",
            action="APPLICATION_SUBMITTED",
            previous_state="DRAFT",
            new_state="Submitted",
            remarks=f"Candidate {c['name']} submitted scholarship application {app_num} under {c['scheme'].code}.",
            stage="Submitted"
        )

        # Block 2: AI OCR & Scrutiny
        log_action(
            db=db,
            application_id=application.id,
            actor_name="MoTA AI-OCR Engine",
            actor_role="system",
            action="AI_VERIFICATION_COMPLETE",
            previous_state="Submitted",
            new_state="Under Verification",
            remarks="Automated document extraction, slot classification, and tampering analysis sealed.",
            stage="Under Verification"
        )

        # Subsequent Blocks based on lifecycle status
        if c["status"] == "Needs Review":
            log_action(
                db=db,
                application_id=application.id,
                actor_name="Desk Officer (Scrutiny Division)",
                actor_role="admin",
                action="DEFICIENCY_NOTICE_RAISED",
                previous_state="Under Verification",
                new_state="Needs Review",
                remarks=c.get("deficiency_reason", "Deficiency notice raised with candidate for document rectification."),
                stage="Needs Review"
            )
        elif c["status"] == "Scrutiny":
            log_action(
                db=db,
                application_id=application.id,
                actor_name="State Level Scrutiny Committee",
                actor_role="admin",
                action="COMMITTEE_ASSIGNED",
                previous_state="Under Verification",
                new_state="Scrutiny",
                remarks=f"Application assigned to {c['scheme'].code} Scrutiny Desk for peer committee evaluation.",
                stage="Scrutiny"
            )
        elif c["status"] == "Selected":
            log_action(
                db=db,
                application_id=application.id,
                actor_name="State Level Scrutiny Committee",
                actor_role="admin",
                action="COMMITTEE_RECOMMENDED",
                previous_state="Under Verification",
                new_state="Scrutiny",
                remarks="Candidate documents certified valid. Recommended for Award Sanction.",
                stage="Scrutiny"
            )
            log_action(
                db=db,
                application_id=application.id,
                actor_name="Dr. R. K. Soren, IAS (Joint Secretary - MoTA)",
                actor_role="admin",
                action="SELECTION_SANCTION_ISSUED",
                previous_state="Scrutiny",
                new_state="Selected",
                remarks=f"Official sanction issued. Disbursal allowance: ₹{c['disb_amount']:,.0f}.",
                stage="Selected"
            )
            log_action(
                db=db,
                application_id=application.id,
                actor_name="PFMS DBT Gateway",
                actor_role="system",
                action="DBT_ACCOUNT_VALIDATED",
                previous_state="Selected",
                new_state="Selected",
                remarks="Aadhaar-seeded bank account validated on PFMS National Clearing Platform.",
                stage="Post-Selection"
            )
        elif c["status"] == "Rejected":
            log_action(
                db=db,
                application_id=application.id,
                actor_name="Selection Committee",
                actor_role="admin",
                action="APPLICATION_REJECTED",
                previous_state="Under Verification",
                new_state="Rejected",
                remarks=c.get("deficiency_reason", "Statutory eligibility criteria breached."),
                stage="Rejected"
            )

    db.commit()

    # -------------------------------------------------------------------------
    # 9. RUN FRAUD & DUPLICATE DETECTION ENGINE FOR ALL APPLICATIONS
    # -------------------------------------------------------------------------
    print("Evaluating fraud & duplicate detection across all seeded applications...")
    for app, c in created_apps:
        risk_result = evaluate_application_risk(app, db)
        app.risk_assessment = risk_result
        app.risk_level = risk_result.get("risk_level", "LOW")
        app.risk_score = risk_result.get("risk_score", 0.0)

    db.commit()

    # -------------------------------------------------------------------------
    # 10. VERIFY IMMUTABLE AUDIT LEDGER INTEGRITY
    # -------------------------------------------------------------------------
    is_valid, broken_links, blocks = verify_chain_integrity(db)
    print(f"Cryptographic Audit Ledger Sealed: Valid={is_valid}, Total Blocks={len(blocks)}, Broken Links={len(broken_links)}")
    print("MoTA Master Database Seeding Completed Successfully!")
