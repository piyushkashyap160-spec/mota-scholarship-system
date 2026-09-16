# MoTA Scholarship & Fellowship Management System
### Ministry of Tribal Affairs (MoTA) | Smart India Hackathon (SIH) Problem Statement 26239

A comprehensive, production-grade digital platform designed for Scheduled Tribe (ST) scholars across India. It modernizes fellowship lifecycle management from registration to post-selection DBT tracking, featuring **schema-driven scheme configurability**, **AI-assisted Tesseract OCR document verification**, **assistive merit ranking**, and five newly integrated enterprise modules:

1. 🛡️ **Duplicate & Fraud Detection Engine** (Cross-application ST certificate collisions, fuzzy name + DOB matching, DBT bank diversion signals, exact SHA-256 file duplicates)
2. 📑 **ML Document Classifier & Wrong-Slot Detector** (Scikit-learn TF-IDF + Naive Bayes pipeline preventing incorrect document uploads)
3. 🔍 **Document Quality & Tampering Signals** (OpenCV Laplacian variance blur scoring, screen photography/moiré analysis, EXIF image-editing suite inspection)
4. 🇮🇳 **India Stack Adapters (DigiLocker + Aadhaar e-KYC + PFMS Tracker)** (Fast-track green path with digitally-signed certificates and 5-stage treasury tracking)
5. ⛓️ **Immutable Cryptographic Audit Trail** (Append-only SHA-256 block hash chains, real-time mathematical integrity verification, and one-click RTI compliance export)

---

## 🏛️ Advanced Architecture & New Modules

### Priority 1: Duplicate & Fraud Detection Engine (`backend/app/fraud_engine.py`)
- **ST Certificate Collisions**: Prevents the same government caste certificate number from being claimed by multiple accounts or across different academic cycles.
- **Fuzzy Name + Date of Birth Deduplication**: Employs `difflib.SequenceMatcher` ($\ge 0.85$ threshold) to catch slight spelling variations (e.g., "Birsa Soren" vs. "Birsa M. Soren") born on the same date.
- **Bank Account Diversion Signals**: Flags multiple applicants sharing the same bank account number (a prime indicator of middleman diversion of Direct Benefit Transfer funds).
- **Forensic Duplicate File Hashes**: Compares SHA-256 document content hashes to flag identical scanned certificates uploaded under different candidate identities.
- **Dual Scheme Enrolment Check**: Flags simultaneous active applications under both domestic fellowship (NFST) and overseas scholarship (NOS).
- **Advisory Risk Scoring**: Assigns point-based risk levels (`LOW`, `MEDIUM`, `HIGH`) with transparent committee justification panels.

### Priority 2: Document Classifier & Wrong-Slot Detection (`backend/app/doc_classifier.py`)
- **Machine Learning Pipeline**: Trained on authentic Indian administrative documents using `TfidfVectorizer` + `MultinomialNB` with cached models in `doc_classifier_model.pkl`.
- **7 Document Classes**: `st_certificate`, `income_certificate`, `admission_letter`, `marksheet`, `bank_passbook`, `aadhaar_card`, `unknown`.
- **Slot Mismatch Prevention**: Displays real-time amber advisory banners if a student mistakenly uploads an Admission Letter into an Income Certificate slot.

### Priority 3: Document Quality & Tampering Signals (`backend/app/ocr_engine.py`)
- **OpenCV Laplacian Variance Sharpness**: Computes edge variance ($\sigma^2 < 100$) to flag blurry scans where official revenue stamps or signatures are unreadable.
- **Resolution Verification**: Checks pixel geometry ($< 800 \times 600$) to ensure statutory archival quality.
- **Screen Photography / Moiré Detection**: 2D Fast Fourier Transform (FFT) high-frequency periodic peak analysis flags mobile photos of computer monitors.
- **EXIF Image Manipulation Detection**: Scans metadata for traces of image editing suites (Adobe Photoshop, GIMP, Canva, CorelDraw).
- **Statutory Safeguard**: Every flag is explicitly labeled: *"ADVISORY SIGNALS FOR HUMAN REVIEW — NOT AN AUTOMATED LEGAL VERDICT"*.

### Priority 4: India Stack Adapters (`backend/app/integrations/`)
- **DigiLocker Integration (`digilocker.py`)**: OAuth2 API Setu gateway with pre-configured tribal student profiles (Birsa Munda [JH], Sunita Soren [OD], Jaipal Oraon [MP]). Issued documents carry $100\%$ confidence and skip manual OCR scrutiny.
- **Aadhaar e-KYC Adapter (`aadhaar_ekyc.py`)**: Simulates UIDAI OTP generation and demographic validation (Sandbox Test OTP: `123456`), locking candidate name, date of birth, and native state.
- **PFMS DBT Tracker (`pfms_tracker.py`)**: 5-stage Public Financial Management System treasury pipeline tracking (Sanction Order $\rightarrow$ PAO Bill Passing $\rightarrow$ NPCI Aadhaar Mapping $\rightarrow$ DBT Initiation $\rightarrow$ Bank Credit with UTR Reference).

### Priority 5: Immutable Cryptographic Audit Trail (`backend/app/audit.py`)
- **SHA-256 Hash Chaining**: Every state transition (Submission, AI Scan, Deficiency Notice, Committee Recommendation, Disbursal Sanction) is cryptographically linked to its parent block hash.
- **Genesis Block Integrity**: Mathematically guarantees that historical scrutiny decisions cannot be rewritten or expunged.
- **RTI Compliance Dossier**: 1-click export of the complete chain in JSON or RFC 4180 CSV formats for Right to Information (RTI) petitions or statutory CAG audits.

---

## 🚀 Quickstart & Setup Guide

### Prerequisites
- Node.js (v18+) & npm
- Python (v3.10 - 3.12 recommended)
- Git

### 1-Click Launch (Windows PowerShell)
From the repository root:
```powershell
.\start_servers.ps1
```

### Manual Start Commands

#### Terminal 1 — Backend (FastAPI):
```powershell
cd backend
.\.venv\Scripts\uvicorn.exe app.main:app --host 127.0.0.1 --port 8000 --reload
```
- API Base URL: `http://127.0.0.1:8000`
- Interactive Swagger API Docs: `http://127.0.0.1:8000/docs`

#### Terminal 2 — Frontend (React + Vite + Tailwind CSS):
```powershell
cd frontend
npm run dev
```
- Frontend Portal URL: `http://127.0.0.1:5173`

---

## 🧪 Automated Test Suite

To run the automated test suite verifying all 5 modules:
```powershell
cd backend
.\.venv\Scripts\python.exe test_all_features.py
```
**Test Results:**
- `test_01_duplicate_and_fraud_engine`: PASS (Detected duplicate ST certificate and shared bank account collisions with 100 pt High Risk score)
- `test_02_document_classifier`: PASS (Correctly identified wrong-slot upload with 94% confidence)
- `test_03_quality_and_tampering_signals`: PASS (Detected OpenCV Laplacian blur and Photoshop editing metadata)
- `test_04_digilocker_aadhaar_pfms`: PASS (DigiLocker profile fetching, Aadhaar OTP demographic verification, 5-stage PFMS tracking)
- `test_05_cryptographic_audit_ledger`: PASS (Verified SHA-256 chain across 52 blocks with 0 broken links; JSON & CSV RTI dossiers valid)

---

## 🔑 Pre-Seeded Demonstrator Test Accounts

The system includes pre-seeded demonstrator accounts for testing each feature:

| Role | Name | Email | Password | Demonstrator Scenario |
| :--- | :--- | :--- | :--- | :--- |
| **Admin** | Dr. R. K. Soren, IAS (MoTA) | `admin@mota.gov.in` | `admin123` | Master scrutiny table, fraud risk badges, cryptographic audit ledger viewer, assistive merit ranking |
| **Applicant (Genuine)** | Birsa Soren | `birsa.soren@research.ac.in` | `scholar123` | **Selected Scholar** (Jharkhand, Santhal) with active DBT fellowship |
| **Applicant (Fraud Demo)** | Birsa M. Soren | `somra.soren@research.in` | `scholar123` | **HIGH RISK Fraud Flag**: Collides with Birsa Soren on ST Certificate (`ST/JH/2023/1029`), Bank Account (`308940029001`), and SHA-256 document hash |
| **Applicant (DigiLocker)** | Birsa Munda | `birsa.munda@tribal-edu.in` | `scholar123` | **DigiLocker Verified Fast-Track**: 100% confidence, issuer-signed certificates, zero manual review needed |
| **Applicant (DigiLocker)** | Sunita Soren | `sunita.soren@tribal-edu.in` | `scholar123` | **DigiLocker Verified** under Committee Scrutiny (Odisha, Santhal) |
| **Applicant (Wrong-Slot)** | Pooja Halba | `pooja.halba@stmail.in` | `scholar123` | **Classifier Slot Mismatch**: Uploaded Ph.D Admission Letter into Annual Income Certificate slot |
| **Applicant (Tamper Demo)** | Priyanka Warli | `priyanka.warli@mu.ac.in` | `scholar123` | **Forensic Quality Signals**: High Laplacian blur ($\sigma^2 = 38.2$), screen moiré pattern, and Photoshop EXIF metadata |
| **Applicant (Deficiency)** | Nehemiah Angami | `nehemiah.angami@manchester.ac.uk` | `scholar123` | **Needs Review**: Conditional offer letter flagged for National Overseas Scholarship (NOS) |
| **Applicant (Ineligible)** | Amit Patra | `amit.patra@stmail.in` | `scholar123` | **Rejected**: General Category candidate falsely declaring ST status |

---

## 📂 Project Structure

```
mota-scholarship-system/
├── backend/
│   ├── app/
│   │   ├── main.py                     # FastAPI entrypoint, CORS, startup seed
│   │   ├── config.py                   # App configuration & paths
│   │   ├── database.py                 # SQLite / PostgreSQL engine
│   │   ├── models.py                   # SQLAlchemy ORM models (AuditLogEntry, Risk, Documents)
│   │   ├── schemas.py                  # Pydantic v2 schemas
│   │   ├── auth.py                     # JWT token & bcrypt hashing
│   │   ├── ocr_engine.py               # Tesseract OCR & OpenCV Laplacian quality signals
│   │   ├── fraud_engine.py             # Duplicate & Fraud detection engine (Priority 1)
│   │   ├── doc_classifier.py           # Scikit-learn TF-IDF classifier (Priority 2)
│   │   ├── audit.py                    # Cryptographic SHA-256 audit ledger (Priority 5)
│   │   ├── eligibility_engine.py       # JSON rulebase qualification engine
│   │   ├── merit_engine.py             # Assistive scoring & ranking algorithm
│   │   ├── seed_data.py                # Comprehensive demonstrator test cases
│   │   ├── integrations/               # India Stack Adapters (Priority 4)
│   │   │   ├── digilocker.py           # DigiLocker issuer integration
│   │   │   ├── aadhaar_ekyc.py         # UIDAI Aadhaar e-KYC OTP simulation
│   │   │   └── pfms_tracker.py         # PFMS DBT disbursement tracker
│   │   └── routes/                     # API routers (auth, schemes, docs, apps, admin, integrations)
│   ├── reseed_db.py                    # Database reseed and chain verification utility
│   ├── test_all_features.py            # End-to-end automated test suite
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/client.js               # API service layer with audit & integration endpoints
│   │   ├── components/                 # Navbar, StatusBadge, DynamicFormRenderer,
│   │   │                               # DocumentUploader, SideBySideOcrViewer, Timeline,
│   │   │                               # FraudRiskPanel, RiskBadge, AuditLedgerViewer,
│   │   │                               # DigiLockerModal, AadhaarKycModal, PfmsDisbursementModal
│   │   └── pages/                      # Home, Login, ApplyScheme, ApplicantDashboard,
│   │                                   # AdminDashboard, AdminApplicationDetail, AdminMeritRanking
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.js
├── start_servers.ps1                   # 1-click startup script
└── README.md
```

---

## 🇮🇳 Statutory Compliance & Disclaimer
All fraud risk scores, document classification tags, and forensic tampering signals generated by this system are advisory algorithmic indicators provided to assist human desk officers and scrutiny committees of the Ministry of Tribal Affairs, Government of India. Administrative decisions and awards comply with official MoTA scheme guidelines and statutory rules.
