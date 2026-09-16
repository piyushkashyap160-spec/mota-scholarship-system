from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from .models import User, Scheme, Application, Document, Deficiency, ActivityLog
from .auth import get_password_hash
from .ocr_engine import cross_verify_document, parse_st_certificate, parse_income_certificate, parse_admission_letter, parse_marksheet
from .eligibility_engine import evaluate_eligibility
from .merit_engine import calculate_merit_score

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

def seed_database(db: Session):
    if db.query(Scheme).first() is not None:
        return
    print("Seeding database...")
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

    nfst = Scheme(
        code="NFST",
        name="NFST - National Fellowship for Scheduled Tribes",
        full_title="National Fellowship and Scholarship for Higher Education of ST Students (Fellowship for M.Phil / Ph.D in India)",
        objective="To provide financial assistance to Scheduled Tribe (ST) students to pursue higher studies like M.Phil and Ph.D in recognized Indian Universities/Institutes.",
        financial_assistance="Junior Research Fellowship (JRF) @ ₹31,000/month; Senior Research Fellowship (SRF) @ ₹35,000/month plus HRA and contingency grants of ₹20,500/year.",
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

    candidates_data = [
        {"name": "Birsa Soren", "email": "birsa.soren@research.ac.in", "state": "Jharkhand", "tribe": "Santhal", "st_cert": "ST/JH/2023/1029", "scheme": nfst, "course": "Ph.D. in Tribal Heritage & Sustainable Sciences", "inst": "Central University of Jharkhand", "marks": 78.5, "income": 240000.0, "status": "Selected", "disb_status": "Active Fellowship Disbursement", "disb_amount": 432000.0, "discrepancy": False},
        {"name": "Anjali Gond", "email": "anjali.gond@iitb.ac.in", "state": "Madhya Pradesh", "tribe": "Gond", "st_cert": "ST/MP/2022/8841", "scheme": nfst, "course": "Ph.D. in Engineering & AI", "inst": "Indian Institute of Technology Bombay", "marks": 82.0, "income": 290000.0, "status": "Selected", "disb_status": "Active Fellowship Disbursement", "disb_amount": 432000.0, "discrepancy": False},
        {"name": "Rupesh Munda", "email": "rupesh.munda@oxford.edu", "state": "Odisha", "tribe": "Munda", "st_cert": "ST/OD/2023/4521", "scheme": nos, "course": "M.Sc. in Global Environmental Change", "inst": "University of Oxford", "marks": 85.4, "income": 360000.0, "status": "Selected", "disb_status": "Tuition & Allowance Sanctioned", "disb_amount": 1850000.0, "discrepancy": False},
        {"name": "Kavita Bodo", "email": "kavita.bodo@gu.ac.in", "state": "Assam", "tribe": "Bodo", "st_cert": "ST/AS/2023/3391", "scheme": nfst, "course": "Ph.D. in Social Sciences", "inst": "Gauhati University", "marks": 74.0, "income": 210000.0, "status": "Selected", "disb_status": "Active Fellowship Disbursement", "disb_amount": 432000.0, "discrepancy": False},
        {"name": "Mangal Oraon", "email": "mangal.oraon@bhu.ac.in", "state": "Chhattisgarh", "tribe": "Oraon", "st_cert": "ST/CG/2024/7712", "scheme": nfst, "course": "Ph.D. in Science & Technology", "inst": "Banaras Hindu University", "marks": 71.5, "income": 310000.0, "status": "Scrutiny", "disb_status": "Pending Committee Sanction", "disb_amount": 0.0, "discrepancy": False},
        {"name": "Grace Nongrum", "email": "grace.nongrum@ed.ac.uk", "state": "Meghalaya", "tribe": "Khasi", "st_cert": "ST/ML/2023/9014", "scheme": nos, "course": "Ph.D. in Public Health", "inst": "University of Edinburgh", "marks": 76.8, "income": 420000.0, "status": "Scrutiny", "disb_status": "Pending Committee Sanction", "disb_amount": 0.0, "discrepancy": False},
        {"name": "Devendra Bhil", "email": "devendra.bhil@uor.ac.in", "state": "Rajasthan", "tribe": "Bhil", "st_cert": "ST/RJ/2023/5129", "scheme": nfst, "course": "Ph.D. in Humanities & Tribal Studies", "inst": "University of Rajasthan", "marks": 69.2, "income": 260000.0, "status": "Under Verification", "disb_status": "In Scrutiny Queue", "disb_amount": 0.0, "discrepancy": False},
        {"name": "Sunita Meena", "email": "sunita.meena@jnu.ac.in", "state": "Rajasthan", "tribe": "Meena", "st_cert": "ST/RJ/2024/6018", "scheme": nfst, "course": "Ph.D. in Social Sciences", "inst": "Jawaharlal Nehru University", "marks": 73.0, "income": 340000.0, "status": "Under Verification", "disb_status": "In Scrutiny Queue", "disb_amount": 0.0, "discrepancy": False},
        {"name": "Sanjay Marandi", "email": "sanjay.marandi@stmail.in", "state": "Jharkhand", "tribe": "Santhal", "st_cert": "ST/JH/2022/9901", "scheme": nfst, "course": "Ph.D. in Science & Technology", "inst": "Ranchi University", "marks": 66.5, "income": 320000.0, "status": "Needs Review", "disb_status": "Deficiency Action Required", "disb_amount": 0.0, "discrepancy": True, "deficiency_doc": "income_certificate", "deficiency_reason": "Income Certificate is for FY 2021-22 instead of current FY 2024-25. Please upload latest Tehsildar verified income certificate.", "mismatch_field": "annual_income", "mismatch_ocr": 520000.0},
        {"name": "Priyanka Warli", "email": "priyanka.warli@mu.ac.in", "state": "Maharashtra", "tribe": "Warli", "st_cert": "ST/MH/2023/4192", "scheme": nfst, "course": "Ph.D. in Tribal Arts & Heritage", "inst": "University of Mumbai", "marks": 70.0, "income": 280000.0, "status": "Needs Review", "disb_status": "Deficiency Action Required", "disb_amount": 0.0, "discrepancy": True, "deficiency_doc": "st_certificate", "deficiency_reason": "ST Certificate scan is low resolution and official issuing stamp is unreadable. Please upload a clear high-res document.", "mismatch_field": "candidate_name", "mismatch_ocr": "Priyanka V. Warli"},
        {"name": "Nehemiah Angami", "email": "nehemiah.angami@manchester.ac.uk", "state": "Nagaland", "tribe": "Angami", "st_cert": "ST/NL/2023/7611", "scheme": nos, "course": "M.Sc. in Data Science", "inst": "University of Manchester", "marks": 72.0, "income": 490000.0, "status": "Needs Review", "disb_status": "Deficiency Action Required", "disb_amount": 0.0, "discrepancy": True, "deficiency_doc": "admission_letter", "deficiency_reason": "Uploaded conditional admission letter. MoTA NOS guidelines require unconditional offer letter. Please re-upload unconditional admission letter.", "mismatch_field": "institution", "mismatch_ocr": "Manchester Metropolitan Univ"},
        {"name": "Lalit Gamit", "email": "lalit.gamit@hngu.ac.in", "state": "Gujarat", "tribe": "Gamit", "st_cert": "ST/GJ/2023/2180", "scheme": nfst, "course": "Ph.D. in Environmental Sciences", "inst": "Hemchandracharya North Gujarat University", "marks": 64.0, "income": 270000.0, "status": "Needs Review", "disb_status": "Deficiency Action Required", "disb_amount": 0.0, "discrepancy": True, "deficiency_doc": "marksheet_masters", "deficiency_reason": "Consolidated marksheet missing Semester 4 transcript. Upload complete transcript copy.", "mismatch_field": "marks_percentage", "mismatch_ocr": 61.2},
        {"name": "Sunil Kharwar", "email": "sunil.kharwar@stmail.in", "state": "Jharkhand", "tribe": "Kharwar", "st_cert": "ST/JH/2024/1109", "scheme": nfst, "course": "Ph.D. in Engineering & AI", "inst": "National Institute of Technology Jamshedpur", "marks": 75.0, "income": 350000.0, "status": "Submitted", "disb_status": "Queued for Verification", "disb_amount": 0.0, "discrepancy": False},
        {"name": "Pooja Halba", "email": "pooja.halba@stmail.in", "state": "Chhattisgarh", "tribe": "Halba", "st_cert": "ST/CG/2024/9931", "scheme": nfst, "course": "Ph.D. in Social Sciences", "inst": "Pandit Ravishankar Shukla University", "marks": 68.0, "income": 250000.0, "status": "Submitted", "disb_status": "Queued for Verification", "disb_amount": 0.0, "discrepancy": False},
        {"name": "Vikram Rathwa", "email": "vikram.rathwa@osu.edu", "state": "Gujarat", "tribe": "Rathwa", "st_cert": "ST/GJ/2024/8802", "scheme": nos, "course": "Ph.D. in Civil Engineering", "inst": "Ohio State University", "marks": 80.5, "income": 580000.0, "status": "Submitted", "disb_status": "Queued for Verification", "disb_amount": 0.0, "discrepancy": False},
        {"name": "Amit Patra", "email": "amit.patra@stmail.in", "state": "Odisha", "tribe": "General Category (Declared as ST)", "st_cert": "GEN/OD/2020/9981", "scheme": nfst, "course": "Ph.D. in Science & Technology", "inst": "Utkal University", "marks": 65.0, "income": 410000.0, "status": "Rejected", "disb_status": "Ineligible", "disb_amount": 0.0, "discrepancy": True, "deficiency_doc": "st_certificate", "deficiency_reason": "Certificate rejected: Candidate belongs to General Category, not listed in Scheduled Tribes list.", "mismatch_field": "community_tribe", "mismatch_ocr": "General / Non-ST"},
        {"name": "Rohan Kumar", "email": "rohan.kumar@stmail.in", "state": "Madhya Pradesh", "tribe": "Bhil", "st_cert": "ST/MP/2021/1102", "scheme": nfst, "course": "Ph.D. in Science & Technology", "inst": "DAVV Indore", "marks": 51.5, "income": 280000.0, "status": "Rejected", "disb_status": "Ineligible", "disb_amount": 0.0, "discrepancy": True, "deficiency_doc": "marksheet_masters", "deficiency_reason": "Academic eligibility criterion violated: Master's score is 51.5% (mandatory cutoff is 55.0%).", "mismatch_field": "marks_percentage", "mismatch_ocr": 51.5},
        {"name": "Deepak Naik", "email": "deepak.naik@stmail.in", "state": "Maharashtra", "tribe": "Gond", "st_cert": "ST/MH/2022/9021", "scheme": nfst, "course": "Ph.D. in Humanities & Tribal Studies", "inst": "Savitribai Phule Pune University", "marks": 63.0, "income": 850000.0, "status": "Rejected", "disb_status": "Ineligible", "disb_amount": 0.0, "discrepancy": True, "deficiency_doc": "income_certificate", "deficiency_reason": "Income ceiling breached: Declared family income ₹8,50,000 exceeds NFST ceiling limit of ₹6,00,000.", "mismatch_field": "annual_income", "mismatch_ocr": 850000.0}
    ]

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
            "dob": "1998-05-12",
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
            "bank_account_no": f"308940029{idx:03d}",
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
            submission_date=datetime.utcnow() - timedelta(days=idx * 2),
            created_at=datetime.utcnow() - timedelta(days=idx * 2)
        )
        db.add(application)
        db.flush()

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
            if c.get("discrepancy") and c.get("deficiency_doc") == dtype:
                doc_status = "Needs Review"
                conf = 52.0

            doc = Document(
                application_id=application.id,
                doc_type=dtype,
                file_name=fname,
                file_path=fpath,
                file_size=245000 + (idx * 15000),
                status=doc_status,
                confidence_score=conf,
                extracted_data=extracted,
                comparison_data=comp_res,
                ocr_text=f"MoTA Scrutiny Intelligence Engine\nDocument: {d_def['title']}\nStatus: {doc_status}",
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

        db.add(ActivityLog(
            application_id=application.id,
            action="Application Submitted",
            actor=c["name"],
            stage="Submitted",
            remarks=f"Application {app_num} submitted successfully.",
            created_at=datetime.utcnow() - timedelta(days=idx * 2)
        ))
        db.add(ActivityLog(
            application_id=application.id,
            action="AI Document Verification Processed",
            actor="MoTA AI-OCR Engine",
            stage="Under Verification",
            remarks="Automated field cross-matching completed.",
            created_at=datetime.utcnow() - timedelta(days=idx * 2, hours=-1)
        ))

        if c["status"] in ["Scrutiny", "Selected", "Needs Review", "Rejected"]:
            db.add(ActivityLog(
                application_id=application.id,
                action="Assigned to Scrutiny Desk",
                actor="Desk Officer",
                stage="Scrutiny",
                remarks="Application queued for committee evaluation.",
                created_at=datetime.utcnow() - timedelta(days=idx, hours=-3)
            ))
        if c["status"] == "Selected":
            db.add(ActivityLog(
                application_id=application.id,
                action="Selection Sanction Issued",
                actor="Joint Secretary (MoTA)",
                stage="Selected",
                remarks=f"Award letter issued. Sanction amount: ₹{c['disb_amount']:,.0f}.",
                created_at=datetime.utcnow() - timedelta(days=1)
            ))
            db.add(ActivityLog(
                application_id=application.id,
                action="DBT Account Configured",
                actor="PFMS Integration",
                stage="Post-Selection",
                remarks="Disbursement account active.",
                created_at=datetime.utcnow()
            ))
        if c["status"] == "Needs Review":
            db.add(ActivityLog(
                application_id=application.id,
                action="Deficiency Notice Raised",
                actor="Scrutiny Officer",
                stage="Needs Review",
                remarks=c.get("deficiency_reason", "Deficiency flagged; resubmission requested."),
                created_at=datetime.utcnow() - timedelta(days=1)
            ))
        if c["status"] == "Rejected":
            db.add(ActivityLog(
                application_id=application.id,
                action="Application Rejected",
                actor="Selection Committee",
                stage="Rejected",
                remarks=c.get("deficiency_reason", "Eligibility criteria breached."),
                created_at=datetime.utcnow() - timedelta(days=1)
            ))

    db.commit()
    print("Database seeding completed successfully!")
