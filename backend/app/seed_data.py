from datetime import datetime, timedelta
import hashlib
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
    if not force and db.query(Scheme).first() is not None:
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

    print("Seeding MoTA Scholarship & Fellowship database...")

    # 1. Admin User
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

    # 2. Scheme 1: NFST
    nfst = Scheme(
        code="NFST",
        name="NFST - National Fellowship for Scheduled Tribes",
        full_title="National Fellowship and Scholarship for Higher Education of ST Students (Fellowship for M.Phil / Ph.D in India)",
        objective="To provide financial assistance to Scheduled Tribe (ST) students to pursue higher studies like M.Phil and Ph.D in recognized Indian Universities/Institutes.",
        financial_assistance="Junior Research Fellowship (JRF) @ ₹31,00,000/year equivalent (₹31,000/month); Senior Research Fellowship (SRF) @ ₹35,000/month plus HRA and contingency grants of ₹20,500/year.",
        target_group="Scheduled Tribe (ST) Research Scholars in India",
        income_ceiling=600000.0,
        min_marks=55.0,
        is_active=True,
        required_documents=[
            {
                "doc_type": "st_certificate",
                "title": "Scheduled Tribe (ST) Certificate",
                "description": "Valid caste certificate issued by Sub-Divisional Magistrate / Tehsildar / Competent Authority.",
                "required": True,
                "target_fields": ["certificate_no", "candidate_name", "sub_caste_tribe", "issuing_authority", "state"]
            },
            {
                "doc_type": "income_certificate",
                "title": "Annual Family Income Certificate",
                "description": "Income certificate for current financial year certifying annual income <= ₹6,00,000.",
                "required": True,
                "target_fields": ["annual_income", "financial_year", "issuing_authority"]
            },
            {
                "doc_type": "admission_letter",
                "title": "Ph.D / M.Phil Admission Letter",
                "description": "Proof of registration or admission offer in an accredited Indian University.",
                "required": True,
                "target_fields": ["institution_name", "course_name", "academic_session"]
            },
            {
                "doc_type": "marksheet_masters",
                "title": "Post-Graduation Marksheet",
                "description": "Final transcript/marksheet of qualifying Master's degree with minimum 55% marks.",
                "required": True,
                "target_fields": ["aggregate_percentage", "passing_year", "university"]
            }
        ],
        eligibility_rules={
            "category_required": "ST",
            "income_ceiling": 600000.0,
            "min_qualifying_percentage": 55.0,
            "eligible_courses": ["Ph.D", "M.Phil", "Doctorate"]
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
            {"id": "course", "label": "Degree / Research Program", "type": "select", "options": ["Ph.D. in Science & Technology", "Ph.D. in Humanities & Tribal Studies", "Ph.D. in Social Sciences", "Ph.D. in Engineering & AI", "M.Phil in Cultural Heritage"], "required": True, "section": "Academic Details"},
            {"id": "institution", "label": "Admitted Institution / University", "type": "text", "required": True, "section": "Academic Details"},
            {"id": "research_topic", "label": "Proposed Research Topic", "type": "textarea", "required": True, "section": "Academic Details"},
            {"id": "marks_percentage", "label": "Master's Degree Aggregate Percentage (%)", "type": "number", "required": True, "section": "Academic Details"},
            {"id": "annual_income", "label": "Annual Family Income (INR ₹)", "type": "number", "required": True, "section": "Financial & Bank Info"},
            {"id": "bank_account_no", "label": "Aadhaar-Linked Bank Account Number", "type": "text", "required": True, "section": "Financial & Bank Info"},
            {"id": "bank_ifsc", "label": "Bank IFSC Code", "type": "text", "required": True, "section": "Financial & Bank Info"},
            {"id": "bank_name", "label": "Bank Name & Branch", "type": "text", "required": True, "section": "Financial & Bank Info"}
        ],
        merit_weights={"marks_weight": 0.70, "income_weight": 0.30}
    )
    db.add(nfst)

    # 3. Scheme 2: NOS
    nos = Scheme(
        code="NOS",
        name="NOS - National Overseas Scholarship",
        full_title="National Overseas Scholarship Scheme for Scheduled Tribe Candidates for Higher Studies Abroad (Master's / Ph.D.)",
        objective="To facilitate low-income Scheduled Tribe scholars in obtaining Master's level courses and Ph.D. degrees from top-500 global universities abroad.",
        financial_assistance="Tuition fee coverage + USD 15,400/year living allowance (or GBP 9,900/year in UK) + return economy airfare + medical insurance.",
        target_group="Scheduled Tribe (ST) Scholars Pursuing Higher Studies Abroad",
        income_ceiling=800000.0,
        min_marks=60.0,
        is_active=True,
        required_documents=[
            {
                "doc_type": "st_certificate",
                "title": "ST Certificate with English Translation",
                "description": "Valid ST certificate issued by competent authority with official seal.",
                "required": True,
                "target_fields": ["certificate_no", "candidate_name", "sub_caste_tribe", "issuing_authority", "state"]
            },
            {
                "doc_type": "income_certificate",
                "title": "Family Income Certificate / Tax Return",
                "description": "Proof certifying total family income <= ₹8,00,000 per annum.",
                "required": True,
                "target_fields": ["annual_income", "financial_year", "issuing_authority"]
            },
            {
                "doc_type": "admission_letter",
                "title": "Unconditional Foreign University Offer Letter",
                "description": "Confirmed admission letter from a QS ranked top-500 global university.",
                "required": True,
                "target_fields": ["institution_name", "course_name", "academic_session"]
            },
            {
                "doc_type": "marksheet_masters",
                "title": "Qualifying Degree Transcripts",
                "description": "Marksheet showing minimum 60% aggregate marks in Bachelor's or Master's degree.",
                "required": True,
                "target_fields": ["aggregate_percentage", "passing_year", "university"]
            }
        ],
        eligibility_rules={
            "category_required": "ST",
            "income_ceiling": 800000.0,
            "min_qualifying_percentage": 60.0,
            "eligible_courses": ["Master's", "Ph.D", "M.S.", "Doctorate"]
        },
        form_fields=[
            {"id": "full_name", "label": "Full Name (as per Passport)", "type": "text", "required": True, "section": "Personal Info"},
            {"id": "father_name", "label": "Father's / Mother's Name", "type": "text", "required": True, "section": "Personal Info"},
            {"id": "passport_no", "label": "Indian Passport Number", "type": "text", "required": True, "section": "Personal Info"},
            {"id": "dob", "label": "Date of Birth", "type": "date", "required": True, "section": "Personal Info"},
            {"id": "state", "label": "Native State", "type": "select", "options": ALL_INDIAN_STATES_AND_UTS, "required": True, "section": "Tribal Verification"},
            {"id": "community_tribe", "label": "Tribal Community", "type": "text", "required": True, "section": "Tribal Verification"},
            {"id": "st_cert_number", "label": "ST Certificate Number", "type": "text", "required": True, "section": "Tribal Verification"},
            {"id": "category", "label": "Category", "type": "text", "required": True, "default": "ST", "read_only": True, "section": "Tribal Verification"},
            {"id": "institution", "label": "Foreign University Name", "type": "text", "required": True, "section": "Overseas Study Details"},
            {"id": "destination_country", "label": "Country of Study", "type": "select", "options": ["United Kingdom", "United States", "Germany", "Canada", "Australia"], "required": True, "section": "Overseas Study Details"},
            {"id": "course", "label": "Overseas Degree & Specialization", "type": "text", "required": True, "section": "Overseas Study Details"},
            {"id": "qs_rank", "label": "QS World University Ranking", "type": "number", "required": True, "section": "Overseas Study Details"},
            {"id": "marks_percentage", "label": "Qualifying Degree Marks (%)", "type": "number", "required": True, "section": "Overseas Study Details"},
            {"id": "annual_income", "label": "Total Family Annual Income (INR ₹)", "type": "number", "required": True, "section": "Financial & Bank Info"},
            {"id": "bank_account_no", "label": "Bank Account Number", "type": "text", "required": True, "section": "Financial & Bank Info"},
            {"id": "bank_ifsc", "label": "Bank IFSC Code", "type": "text", "required": True, "section": "Financial & Bank Info"}
        ],
        merit_weights={"marks_weight": 0.75, "income_weight": 0.25}
    )
    db.add(nos)
    db.flush()

    # 4. Candidates with Demonstrator Test Cases
    candidates_data = [
        # Candidate 1: Authentic Selected Scholar (Jharkhand, Santhal)
        {
            "name": "Birsa Soren",
            "email": "birsa.soren@research.ac.in",
            "state": "Jharkhand",
            "tribe": "Santhal",
            "st_cert": "ST/JH/2023/1029",
            "scheme": nfst,
            "course": "Ph.D. in Tribal Heritage & Sustainable Sciences",
            "inst": "Central University of Jharkhand",
            "marks": 78.5,
            "income": 240000.0,
            "status": "Selected",
            "disb_status": "Active Fellowship Disbursement",
            "disb_amount": 432000.0,
            "bank_account": "308940029001",
            "dob": "1998-05-12",
            "discrepancy": False,
            "file_hash_st": "a1b2c3d4e5f60718293a4b5c6d7e8f90123456789abcdef0123456789abcdef0"
        },
        # Candidate 2: FRAUD ENGINE DEMO (Collides with Birsa Soren: Duplicate ST Cert + Bank + Identity similarity)
        {
            "name": "Birsa M. Soren",
            "email": "somra.soren@research.in",
            "state": "Jharkhand",
            "tribe": "Santhal",
            "st_cert": "ST/JH/2023/1029",  # DUPLICATE ST CERTIFICATE!
            "scheme": nfst,
            "course": "Ph.D. in Science & Technology",
            "inst": "Ranchi University",
            "marks": 71.0,
            "income": 250000.0,
            "status": "Needs Review",
            "disb_status": "Flagged by Fraud Engine",
            "disb_amount": 0.0,
            "bank_account": "308940029001",  # DUPLICATE BANK ACCOUNT!
            "dob": "1998-05-12",  # IDENTICAL DOB!
            "discrepancy": True,
            "deficiency_doc": "st_certificate",
            "deficiency_reason": "High fraud risk: ST Certificate number ST/JH/2023/1029 and DBT bank account are already registered in another active application.",
            "file_hash_st": "a1b2c3d4e5f60718293a4b5c6d7e8f90123456789abcdef0123456789abcdef0"  # IDENTICAL HASH!
        },
        # Candidate 3: DIGILOCKER PRE-VERIFIED DEMO 1 (Green Fast-Track, Birsa Munda)
        {
            "name": "Birsa Munda",
            "email": "birsa.munda@tribal-edu.in",
            "state": "Jharkhand",
            "tribe": "Munda",
            "st_cert": "ST/JH/2024/9912",
            "scheme": nfst,
            "course": "Ph.D. in Sustainable Forestry & Tribal Ecology",
            "inst": "Birsa Agricultural University",
            "marks": 84.5,
            "income": 180000.0,
            "status": "Selected",
            "disb_status": "Active Fellowship Disbursement",
            "disb_amount": 432000.0,
            "bank_account": "308940029003",
            "dob": "1997-11-15",
            "is_digilocker": True,
            "is_aadhaar": True,
            "discrepancy": False
        },
        # Candidate 4: DIGILOCKER PRE-VERIFIED DEMO 2 (Sunita Soren, Odisha)
        {
            "name": "Sunita Soren",
            "email": "sunita.soren@tribal-edu.in",
            "state": "Odisha",
            "tribe": "Santhal",
            "st_cert": "ST/OD/2024/8801",
            "scheme": nfst,
            "course": "Ph.D. in Humanities & Tribal Studies",
            "inst": "Utkal University",
            "marks": 81.0,
            "income": 220000.0,
            "status": "Scrutiny",
            "disb_status": "Pending Committee Sanction",
            "disb_amount": 0.0,
            "bank_account": "308940029004",
            "dob": "1999-03-22",
            "is_digilocker": True,
            "is_aadhaar": True,
            "discrepancy": False
        },
        # Candidate 5: DOCUMENT CLASSIFIER DEMO (Wrong-Slot Upload: Admission Letter in Income slot)
        {
            "name": "Pooja Halba",
            "email": "pooja.halba@stmail.in",
            "state": "Chhattisgarh",
            "tribe": "Halba",
            "st_cert": "ST/CG/2024/9931",
            "scheme": nfst,
            "course": "Ph.D. in Social Sciences",
            "inst": "Pandit Ravishankar Shukla University",
            "marks": 68.0,
            "income": 250000.0,
            "status": "Needs Review",
            "disb_status": "Deficiency Action Required",
            "disb_amount": 0.0,
            "bank_account": "308940029005",
            "dob": "2000-08-19",
            "discrepancy": True,
            "wrong_slot_demo": True,
            "deficiency_doc": "income_certificate",
            "deficiency_reason": "Slot Mismatch: Uploaded document in Income Certificate slot is identified by AI as an Admission Offer Letter. Please upload the valid Tehsil Income Certificate."
        },
        # Candidate 6: TAMPERING & QUALITY DEMO (OpenCV Blur + Moiré + Photoshop metadata)
        {
            "name": "Priyanka Warli",
            "email": "priyanka.warli@mu.ac.in",
            "state": "Maharashtra",
            "tribe": "Warli",
            "st_cert": "ST/MH/2023/4192",
            "scheme": nfst,
            "course": "Ph.D. in Tribal Arts & Heritage",
            "inst": "University of Mumbai",
            "marks": 70.0,
            "income": 280000.0,
            "status": "Needs Review",
            "disb_status": "Deficiency Action Required",
            "disb_amount": 0.0,
            "bank_account": "308940029006",
            "dob": "1999-01-14",
            "discrepancy": True,
            "tamper_demo": True,
            "deficiency_doc": "st_certificate",
            "deficiency_reason": "Authenticity Advisory: Document exhibits high blur (Laplacian variance 38.2), screen photography moiré patterns, and Adobe Photoshop editing metadata. Clear original scan required."
        },
        # Candidate 7: National Overseas Scholarship (Oxford University, Selected)
        {
            "name": "Rupesh Munda",
            "email": "rupesh.munda@oxford.edu",
            "state": "Odisha",
            "tribe": "Munda",
            "st_cert": "ST/OD/2023/4521",
            "scheme": nos,
            "course": "M.Sc. in Global Environmental Change",
            "inst": "University of Oxford",
            "marks": 85.4,
            "income": 360000.0,
            "status": "Selected",
            "disb_status": "Tuition & Allowance Sanctioned",
            "disb_amount": 1850000.0,
            "bank_account": "308940029007",
            "dob": "1996-07-28",
            "discrepancy": False
        },
        # Candidate 8: IIT Bombay Research Scholar (Gond Tribe, Selected)
        {
            "name": "Anjali Gond",
            "email": "anjali.gond@iitb.ac.in",
            "state": "Madhya Pradesh",
            "tribe": "Gond",
            "st_cert": "ST/MP/2022/8841",
            "scheme": nfst,
            "course": "Ph.D. in Engineering & AI",
            "inst": "Indian Institute of Technology Bombay",
            "marks": 82.0,
            "income": 290000.0,
            "status": "Selected",
            "disb_status": "Active Fellowship Disbursement",
            "disb_amount": 432000.0,
            "bank_account": "308940029008",
            "dob": "1997-09-04",
            "discrepancy": False
        },
        # Candidate 9: University of Edinburgh (NOS Scheme, Scrutiny)
        {
            "name": "Grace Nongrum",
            "email": "grace.nongrum@ed.ac.uk",
            "state": "Meghalaya",
            "tribe": "Khasi",
            "st_cert": "ST/ML/2023/9014",
            "scheme": nos,
            "course": "Ph.D. in Public Health",
            "inst": "University of Edinburgh",
            "marks": 76.8,
            "income": 420000.0,
            "status": "Scrutiny",
            "disb_status": "Pending Committee Sanction",
            "disb_amount": 0.0,
            "bank_account": "308940029009",
            "dob": "1998-12-10",
            "discrepancy": False
        },
        # Candidate 10: Banaras Hindu University (Scrutiny)
        {
            "name": "Mangal Oraon",
            "email": "mangal.oraon@bhu.ac.in",
            "state": "Chhattisgarh",
            "tribe": "Oraon",
            "st_cert": "ST/CG/2024/7712",
            "scheme": nfst,
            "course": "Ph.D. in Science & Technology",
            "inst": "Banaras Hindu University",
            "marks": 71.5,
            "income": 310000.0,
            "status": "Scrutiny",
            "disb_status": "Pending Committee Sanction",
            "disb_amount": 0.0,
            "bank_account": "308940029010",
            "dob": "1999-04-18",
            "discrepancy": False
        },
        # Candidate 11: Rajasthan Domicile (Bhil Tribe, Under Verification)
        {
            "name": "Devendra Bhil",
            "email": "devendra.bhil@uor.ac.in",
            "state": "Rajasthan",
            "tribe": "Bhil",
            "st_cert": "ST/RJ/2023/5129",
            "scheme": nfst,
            "course": "Ph.D. in Humanities & Tribal Studies",
            "inst": "University of Rajasthan",
            "marks": 69.2,
            "income": 260000.0,
            "status": "Under Verification",
            "disb_status": "In Scrutiny Queue",
            "disb_amount": 0.0,
            "bank_account": "308940029011",
            "dob": "2000-02-11",
            "discrepancy": False
        },
        # Candidate 12: NOS Conditional Admission Deficiency (Nagaland, Angami)
        {
            "name": "Nehemiah Angami",
            "email": "nehemiah.angami@manchester.ac.uk",
            "state": "Nagaland",
            "tribe": "Angami",
            "st_cert": "ST/NL/2023/7611",
            "scheme": nos,
            "course": "M.Sc. in Data Science",
            "inst": "University of Manchester",
            "marks": 72.0,
            "income": 490000.0,
            "status": "Needs Review",
            "disb_status": "Deficiency Action Required",
            "disb_amount": 0.0,
            "bank_account": "308940029012",
            "dob": "1998-06-30",
            "discrepancy": True,
            "deficiency_doc": "admission_letter",
            "deficiency_reason": "Conditional admission offer uploaded. MoTA NOS guidelines mandate unconditional offer letter.",
            "mismatch_field": "institution",
            "mismatch_ocr": "Manchester Metropolitan Univ"
        },
        # Candidate 13: Ineligible Category Breach (General candidate falsely claiming ST)
        {
            "name": "Amit Patra",
            "email": "amit.patra@stmail.in",
            "state": "Odisha",
            "tribe": "General Category (Declared as ST)",
            "st_cert": "GEN/OD/2020/9981",
            "scheme": nfst,
            "course": "Ph.D. in Science & Technology",
            "inst": "Utkal University",
            "marks": 65.0,
            "income": 410000.0,
            "status": "Rejected",
            "disb_status": "Ineligible",
            "disb_amount": 0.0,
            "bank_account": "308940029013",
            "dob": "1997-10-12",
            "discrepancy": True,
            "deficiency_doc": "st_certificate",
            "deficiency_reason": "Certificate rejected: Candidate belongs to General Category, not listed in Scheduled Tribes presidential order.",
            "mismatch_field": "community_tribe",
            "mismatch_ocr": "General / Non-ST"
        },
        # Candidate 14: Ineligible Cutoff Breach (51.5% marks below mandatory 55%)
        {
            "name": "Rohan Kumar",
            "email": "rohan.kumar@stmail.in",
            "state": "Madhya Pradesh",
            "tribe": "Bhil",
            "st_cert": "ST/MP/2021/1102",
            "scheme": nfst,
            "course": "Ph.D. in Science & Technology",
            "inst": "DAVV Indore",
            "marks": 51.5,
            "income": 280000.0,
            "status": "Rejected",
            "disb_status": "Ineligible",
            "disb_amount": 0.0,
            "bank_account": "308940029014",
            "dob": "1999-05-20",
            "discrepancy": True,
            "deficiency_doc": "marksheet_masters",
            "deficiency_reason": "Academic eligibility criteria violated: Master's score is 51.5% (mandatory cutoff is 55.0%).",
            "mismatch_field": "marks_percentage",
            "mismatch_ocr": 51.5
        },
        # Candidate 15: Ineligible Income Ceiling Breach (₹8.5L exceeds ₹6L limit)
        {
            "name": "Deepak Naik",
            "email": "deepak.naik@stmail.in",
            "state": "Maharashtra",
            "tribe": "Gond",
            "st_cert": "ST/MH/2022/9021",
            "scheme": nfst,
            "course": "Ph.D. in Humanities & Tribal Studies",
            "inst": "Savitribai Phule Pune University",
            "marks": 63.0,
            "income": 850000.0,
            "status": "Rejected",
            "disb_status": "Ineligible",
            "disb_amount": 0.0,
            "bank_account": "308940029015",
            "dob": "1998-03-14",
            "discrepancy": True,
            "deficiency_doc": "income_certificate",
            "deficiency_reason": "Income ceiling breached: Family income ₹8,50,000 exceeds NFST ceiling limit of ₹6,00,000.",
            "mismatch_field": "annual_income",
            "mismatch_ocr": 850000.0
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
            "father_name": f"{c['name'].split()[0]}'s Father",
            "gender": "Male" if idx % 2 == 1 else "Female",
            "dob": c.get("dob", "1998-05-12"),
            "phone": user.phone,
            "state": c["state"],
            "community_tribe": c["tribe"],
            "st_cert_number": c["st_cert"],
            "category": "ST" if "General" not in c["tribe"] else "GEN",
            "course": c["course"],
            "degree_level": "Ph.D" if "Ph.D" in c["course"] else "Master's",
            "institution": c["inst"],
            "research_topic": f"Empirical Study on Tribal Heritage and Sustainable Growth in {c['state']}",
            "marks_percentage": c["marks"],
            "annual_income": c["income"],
            "bank_account_no": c.get("bank_account", f"308940029{idx:03d}"),
            "bank_ifsc": "SBIN0001234",
            "bank_name": "State Bank of India",
            "passport_no": f"T{892010 + idx}" if c["scheme"].code == "NOS" else None
        }

        is_eligible, notes, breakdown = evaluate_eligibility(c["scheme"].eligibility_rules, form_data)
        merit_score = calculate_merit_score(form_data, income_ceiling=c["scheme"].income_ceiling)

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

        req_docs = c["scheme"].required_documents or []
        for d_def in req_docs:
            dtype = d_def["doc_type"]
            fname = f"{dtype}_{app_num.lower()}.pdf"
            fpath = f"/uploads/{fname}"

            extracted = {}
            if dtype == "st_certificate":
                extracted = parse_st_certificate(f"Certificate No: {c['st_cert']}\nName: {c['name']}\nTribe: {c['tribe']}", form_data)
                if c.get("discrepancy") and c.get("mismatch_field") == "candidate_name":
                    extracted["candidate_name"] = c["mismatch_ocr"]
            elif dtype == "income_certificate":
                extracted = parse_income_certificate(f"Income certificate certifying Rs. {c['income']:.0f} per annum", form_data)
                if c.get("discrepancy") and c.get("mismatch_field") == "annual_income":
                    extracted["annual_income"] = c["mismatch_ocr"]
            elif dtype == "admission_letter":
                extracted = parse_admission_letter(f"Admission to {c['inst']}", form_data)
                if c.get("discrepancy") and c.get("mismatch_field") == "institution":
                    extracted["institution_name"] = c["mismatch_ocr"]
            elif dtype == "marksheet_masters":
                extracted = parse_marksheet(f"Aggregate marks: {c['marks']}%", form_data)
                if c.get("discrepancy") and c.get("mismatch_field") == "marks_percentage":
                    extracted["aggregate_percentage"] = c["mismatch_ocr"]
            else:
                extracted = {"valid": True, "type": dtype}

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

        # Standard Activity Logs
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

        # 5. CRYPTOGRAPHIC AUDIT LEDGER (Priority 5 Genesis & Chained Blocks)
        # Block 1: Application Submission
        log_action(
            db=db,
            application_id=application.id,
            actor_name=c["name"],
            actor_role="applicant",
            action="APPLICATION_SUBMITTED",
            previous_state="DRAFT",
            new_state="Submitted",
            remarks=f"Candidate {c['name']} submitted scholarship application {app_num}.",
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
                remarks="Application assigned to National Fellowship Scrutiny Desk for peer evaluation.",
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
                remarks="Candidate documents certified valid. Recommended for National Fellowship Award.",
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

    # 6. RUN FRAUD & DUPLICATE DETECTION ENGINE FOR ALL APPLICATIONS
    print("Evaluating fraud & duplicate detection across seeded applications...")
    for app, c in created_apps:
        risk_result = evaluate_application_risk(app, db)
        app.risk_assessment = risk_result
        app.risk_level = risk_result.get("risk_level", "LOW")
        app.risk_score = risk_result.get("risk_score", 0.0)

    db.commit()

    # 7. VERIFY AUDIT LEDGER INTEGRITY
    is_valid, broken_links, blocks = verify_chain_integrity(db)
    print(f"Cryptographic Audit Ledger Sealed: Valid={is_valid}, Total Blocks={len(blocks)}")
    print("Database seeding completed successfully!")
