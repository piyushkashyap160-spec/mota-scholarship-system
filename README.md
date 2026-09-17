# MoTA Scholarship & Fellowship Management System
### Ministry of Tribal Affairs (MoTA) | Smart India Hackathon (SIH) Problem Statement 26239

A comprehensive, production-grade digital platform designed for Scheduled Tribe (ST) scholars across India. It modernizes fellowship lifecycle management from registration to post-selection DBT tracking, featuring **schema-driven scheme configurability**, **AI-assisted Tesseract OCR document verification**, **assistive merit ranking**, and advanced enterprise capabilities:

1. 🛡️ **Duplicate & Fraud Detection Engine** (Cross-application ST certificate collisions, fuzzy name + DOB matching, DBT bank diversion signals, exact SHA-256 file duplicates)
2. 📑 **ML Document Classifier & Wrong-Slot Detector** (Scikit-learn TF-IDF + Naive Bayes pipeline preventing incorrect document uploads)
3. 🔍 **Document Quality & Tampering Signals** (OpenCV Laplacian variance blur scoring, screen photography/moiré analysis, EXIF image-editing suite inspection)
4. 🇮🇳 **India Stack Adapters (DigiLocker + Aadhaar e-KYC + PFMS Tracker)** (Fast-track green path with digitally-signed certificates and 5-stage treasury tracking)
5. ⛓️ **Immutable Cryptographic Audit Trail** (Append-only SHA-256 block hash chains, real-time mathematical integrity verification, and one-click RTI compliance export)
6. 🔔 **Email & SMS Notification Engine** (Real SMTP delivery with simulated console + audit log fallback; fires on submission, deficiency, and award events)
7. ⚙️ **Admin Scheme Rule Editor** (In-place eligibility rulebase customization for income ceilings, qualifying marks, and quotas with full cryptographic change-logging)
8. 🔐 **Self-Service Password Reset & OTP Recovery** (Cryptographically signed 6-digit OTP verification with expiration safety and inline recovery UI)
9. 🔄 **Fellowship Annual Renewal Workflow** (Multi-year continuation for NFST 5-yr & NOS 3-yr awards, annual progress reporting, and automatic +365 day stipend extensions)
10. 🏫 **Institution Nodal Officer Role & Verification Desk** (University-level enrollment verification prerequisite before ministry scrutiny with dedicated nodal dashboards)

---

## 🏛️ Advanced Architecture & Feature Modules

### 1. Duplicate & Fraud Detection Engine (`backend/app/fraud_engine.py`)
- **ST Certificate Collisions**: Prevents the same government caste certificate number from being claimed by multiple accounts or across different academic cycles.
- **Fuzzy Name + Date of Birth Deduplication**: Employs `difflib.SequenceMatcher` ($\ge 0.85$ threshold) to catch slight spelling variations (e.g., "Birsa Soren" vs. "Birsa M. Soren") born on the same date.
- **Bank Account Diversion Signals**: Flags multiple applicants sharing the same bank account number (a prime indicator of middleman diversion of Direct Benefit Transfer funds).
- **Forensic Duplicate File Hashes**: Compares SHA-256 document content hashes to flag identical scanned certificates uploaded under different candidate identities.
- **Dual Scheme Enrolment Check**: Flags simultaneous active applications under both domestic fellowship (NFST) and overseas scholarship (NOS).
- **Advisory Risk Scoring**: Assigns point-based risk levels (`LOW`, `MEDIUM`, `HIGH`) with transparent committee justification panels.

### 2. Document Classifier & Wrong-Slot Detection (`backend/app/doc_classifier.py`)
- **Machine Learning Pipeline**: Trained on authentic Indian administrative documents using `TfidfVectorizer` + `MultinomialNB` with cached models in `doc_classifier_model.pkl`.
- **7 Document Classes**: `st_certificate`, `income_certificate`, `admission_letter`, `marksheet`, `bank_passbook`, `aadhaar_card`, `unknown`.
- **Slot Mismatch Prevention**: Displays real-time amber advisory banners if a student mistakenly uploads an Admission Letter into an Income Certificate slot.

### 3. Document Quality & Tampering Signals (`backend/app/ocr_engine.py`)
- **OpenCV Laplacian Variance Sharpness**: Computes edge variance ($\sigma^2 < 100$) to flag blurry scans where official revenue stamps or signatures are unreadable.
- **Resolution Verification**: Checks pixel geometry ($< 800 \times 600$) to ensure statutory archival quality.
- **Screen Photography / Moiré Detection**: 2D Fast Fourier Transform (FFT) high-frequency periodic peak analysis flags mobile photos of computer monitors.
- **EXIF Image Manipulation Detection**: Scans metadata for traces of image editing suites (Adobe Photoshop, GIMP, Canva, CorelDraw).
- **Statutory Safeguard**: Every flag is explicitly labeled: *"ADVISORY SIGNALS FOR HUMAN REVIEW — NOT AN AUTOMATED LEGAL VERDICT"*.

### 4. India Stack Adapters (`backend/app/integrations/`)
- **DigiLocker Integration (`digilocker.py`)**: OAuth2 API Setu gateway with pre-configured tribal student profiles (Birsa Munda [JH], Sunita Soren [OD], Jaipal Oraon [MP]). Issued documents carry $100\%$ confidence and skip manual OCR scrutiny.
- **Aadhaar e-KYC Adapter (`aadhaar_ekyc.py`)**: Simulates UIDAI OTP generation and demographic validation (Sandbox Test OTP: `123456`), locking candidate name, date of birth, and native state.
- **PFMS DBT Tracker (`pfms_tracker.py`)**: 5-stage Public Financial Management System treasury pipeline tracking (Sanction Order $\rightarrow$ PAO Bill Passing $\rightarrow$ NPCI Aadhaar Mapping $\rightarrow$ DBT Initiation $\rightarrow$ Bank Credit with UTR Reference).

### 5. Immutable Cryptographic Audit Trail (`backend/app/audit.py`)
- **SHA-256 Hash Chaining**: Every state transition (Submission, AI Scan, Deficiency Notice, Committee Recommendation, Disbursal Sanction) is cryptographically linked to its parent block hash.
- **Genesis Block Integrity**: Mathematically guarantees that historical scrutiny decisions cannot be rewritten or expunged.
- **RTI Compliance Dossier**: 1-click export of the complete chain in JSON or RFC 4180 CSV formats for Right to Information (RTI) petitions or statutory CAG audits.

### 6. Email & SMS Notification Engine (`backend/app/notifications.py`)
- **Multi-Transport Communication**: Dispatches real emails via standard Python `smtplib` if SMTP credentials are provided in `.env` (`SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`), falling back gracefully to a simulated ledger for demonstration and judging.
- **Automated Lifecycle Triggers**:
  - Application submission confirmation with tracking number.
  - Officer deficiency notices with required document name and remarks.
  - Selection and fellowship award sanction letters with approved amount.
  - University nodal enrollment sign-off notices.
- **Admin Communications Ledger**: Dedicated real-time notification inspector panel on the Admin Scrutiny Dashboard showing dispatch timestamp, recipient, subject, preview, and delivery status (`SENT` or `SIMULATED`).

### 7. Admin Scheme Rule Editor (`backend/app/routes/scheme_routes.py`)
- **In-Place Threshold Management**: Allows authorized MoTA admins to update scheme parameters (annual family income ceiling, minimum academic marks percentage, target slots, and guidelines) via `PUT /api/schemes/{id}`.
- **Cryptographic Audit Integration**: Every rule amendment creates an immutable entry in the SHA-256 cryptographic audit ledger recording previous vs. new values and the officer's identity.
- **Interactive Modal (`SchemeEditor.jsx`)**: Clean administrative interface accessible directly from the Scheme Volume distribution cards on the admin portal.

### 8. Self-Service Password Reset & OTP Recovery (`backend/app/routes/auth_routes.py`)
- **Secure 6-Digit Token Generation**: Generates cryptographically random 6-digit OTPs with a 15-minute expiration window stored in `password_reset_tokens`.
- **2-Step Inline Modal**: Applicant enters registered email $\rightarrow$ receives OTP via notification dispatch $\rightarrow$ verifies OTP and sets new password with instant bcrypt hash updating.
- **Pre-Seeded Demo OTP**: Seeded demo token `482910` for immediate evaluation on `birsa.soren@research.ac.in`.

### 9. Fellowship Annual Renewal Workflow (`backend/app/routes/application_routes.py`)
- **Multi-Year Continuation**: Supports continuous multi-year fellowships (NFST is up to 5 years, NOS is up to 3 years) through linked applications (`parent_application_id`).
- **Applicant Continuation Desk**: Approaching renewal dates trigger an alert banner on the scholar dashboard allowing one-click submission of annual academic progress reports, current semester details, and supervisor verification.
- **Administrative Extension**: Admin approval of a renewal submission extends the fellowship award by exactly +365 days (`renewal_due_date`), records the change on the parent application, and logs it to the audit ledger.

### 10. Institution Nodal Officer Role & Verification Desk (`backend/app/routes/institution_routes.py`)
- **Role-Based Institution Access**: New `role="institution"` user persona with dedicated University Nodal Verification Desk (`InstitutionDashboard.jsx`).
- **Affiliated Student Queue**: Automatically scopes student applications matching the officer's institution name (e.g., IIT Delhi, Central University of Jharkhand).
- **Mandatory Prerequisite Sign-Off**: Verification checks enrollment against university registers. If confirmed enrolled, the application advances to Ministry Scrutiny; if flagged not enrolled, it automatically enters `Needs Review` with a student notification.
- **Scrutiny Desk Badges**: Real-time "Institution Verified" (green check) vs. "Pending Sign-off" (amber clock) indicators across the admin application table and detailed review views.

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

To run the comprehensive test suite verifying all system capabilities:
```powershell
cd backend
.\.venv\Scripts\python.exe test_all_features.py
```

**Verified Capabilities:**
- Duplicate & Fraud Engine: Caught duplicate ST certificate and shared bank account collisions with High Risk flags.
- Document Classifier: ML classifier detected wrong-slot uploads with $>90\%$ confidence.
- Document Forensics: Detected OpenCV Laplacian blur and Photoshop editing EXIF markers.
- India Stack Adapters: Verified DigiLocker instant certificates, Aadhaar e-KYC sandbox OTP, and 5-stage PFMS treasury tracking.
- Cryptographic Audit Trail: Verified SHA-256 chain integrity across all historical blocks with 0 broken links; JSON and CSV RTI compliance export verified.
- Notifications: Dispatched simulated emails and SMS records with database logging.
- Rule Editor: Successfully updated scheme income and marks thresholds and verified audit logs.
- Password Reset: Verified OTP generation, verification, and bcrypt password updates.
- Fellowship Renewal: Tested renewal submission, linked parent tracking, and +365 day due date extension.
- Institution Verification: Tested university-level queue scoping, enrollment verification, and prerequisite enforcement.

---

## 🔑 Pre-Seeded Demonstrator Test Accounts

The platform includes pre-seeded demonstrator accounts for testing every persona (accessible via the 1-click **Demo Role** dropdown in the navigation bar or on the login page):

| Role | Name | Email | Password | Demonstrator Scenario |
| :--- | :--- | :--- | :--- | :--- |
| **MoTA Admin** | Dr. R. K. Soren, IAS (MoTA) | `admin@mota.gov.in` | `admin123` | Master scrutiny table, scheme rule editor, fraud risk badges, cryptographic audit ledger, notification logs, merit ranking |
| **ST Applicant** | Birsa Soren | `birsa.soren@research.ac.in` | `scholar123` | **Selected Scholar** (Jharkhand, Santhal) with active fellowship, renewal due banner, and active demo reset OTP (`482910`) |
| **ST Applicant** | Pooja Halba | `pooja.halba@stmail.in` | `scholar123` | **Deficiency Resubmission**: Active document deficiency ready for rectified upload and re-scrutiny |
| **ST Applicant** | Birsa M. Soren | `somra.soren@research.in` | `scholar123` | **HIGH RISK Fraud Flag**: Collides with Birsa Soren on ST Certificate (`ST/JH/2023/1029`), Bank Account (`308940029001`), and SHA-256 file hash |
| **Institution Officer** | Prof. Arvind Meena | `nodal@iitd.ac.in` | `nodal123` | **IIT Delhi Nodal Desk**: Verify and sign off enrolled scholars at IIT Delhi |
| **Institution Officer** | Dr. Sushila Oraon | `nodal@cuj.ac.in` | `nodal123` | **CUJ Nodal Desk**: Verify and sign off enrolled scholars at Central University of Jharkhand |

---

## 📂 Project Structure

```
mota-scholarship-system/
├── backend/
│   ├── app/
│   │   ├── main.py                     # FastAPI entrypoint, CORS, startup seed
│   │   ├── config.py                   # App configuration & .env loading
│   │   ├── database.py                 # SQLAlchemy SQLite / PostgreSQL engine
│   │   ├── models.py                   # SQLAlchemy ORM models (Users, Schemes, Apps, Verifications, Notifications)
│   │   ├── schemas.py                  # Pydantic v2 schemas
│   │   ├── auth.py                     # JWT auth & role guards (admin, applicant, institution)
│   │   ├── notifications.py            # Email & SMS notification service with simulation fallback
│   │   ├── ocr_engine.py               # Tesseract OCR & OpenCV Laplacian quality signals
│   │   ├── fraud_engine.py             # Duplicate & Fraud detection engine
│   │   ├── doc_classifier.py           # Scikit-learn TF-IDF classifier
│   │   ├── audit.py                    # Cryptographic SHA-256 audit ledger
│   │   ├── eligibility_engine.py       # JSON rulebase qualification engine with institution checks
│   │   ├── merit_engine.py             # Assistive scoring & ranking algorithm
│   │   ├── seed_data.py                # Comprehensive demonstrator test cases & seeds
│   │   ├── integrations/               # India Stack Adapters
│   │   │   ├── digilocker.py           # DigiLocker issuer integration
│   │   │   ├── aadhaar_ekyc.py         # UIDAI Aadhaar e-KYC OTP simulation
│   │   │   └── pfms_tracker.py         # PFMS DBT disbursement tracker
│   │   └── routes/                     # API routers
│   │       ├── auth_routes.py          # Login, registration, forgot-password, reset-password
│   │       ├── scheme_routes.py        # Scheme listings & Admin Rule Editor (PUT /api/schemes/{id})
│   │       ├── document_routes.py      # Tesseract OCR scanning & quality inspection
│   │       ├── application_routes.py   # Application lifecycle, resubmission, and annual renewals
│   │       ├── admin_routes.py         # Administrative scrutiny, actions, merit ranking, and notification logs
│   │       ├── integration_routes.py   # DigiLocker, Aadhaar e-KYC, PFMS DBT tracking
│   │       └── institution_routes.py   # University Nodal Officer verification queue & sign-offs
│   ├── reseed_db.py                    # Database reseed and chain verification utility
│   ├── test_all_features.py            # End-to-end automated test suite
│   ├── .env.example                    # Sample SMTP and system environment variables
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/client.js               # API service layer covering all backend routes
│   │   ├── components/                 # Reusable UI components
│   │   │   ├── Navbar.jsx              # Brand header, role badge & 4-way persona switcher
│   │   │   ├── StatusBadge.jsx         # Status badges
│   │   │   ├── RiskBadge.jsx           # Fraud risk level badges
│   │   │   ├── DynamicFormRenderer.jsx # Configurable scheme application forms
│   │   │   ├── DocumentUploader.jsx    # Drag-and-drop OCR upload
│   │   │   ├── SideBySideOcrViewer.jsx # Dual-pane document verification matrix
│   │   │   ├── Timeline.jsx            # 5-stage progress timeline
│   │   │   ├── FraudRiskPanel.jsx      # Detailed advisory risk inspection card
│   │   │   ├── AuditLedgerViewer.jsx   # SHA-256 block chain inspector with RTI export
│   │   │   ├── SchemeEditor.jsx        # Admin modal for live eligibility threshold updates
│   │   │   ├── RenewalModal.jsx        # Annual fellowship continuation submission modal
│   │   │   ├── DigiLockerModal.jsx     # DigiLocker green-channel verification modal
│   │   │   ├── AadhaarKycModal.jsx     # UIDAI Aadhaar e-KYC verification modal
│   │   │   └── PfmsDisbursementModal.jsx # PFMS DBT 5-stage treasury tracking modal
│   │   └── pages/                      # Page views
│   │       ├── Home.jsx                # Scheme catalog & portal overview
│   │       ├── Login.jsx               # Sign in, ST registration, forgot password, 1-click demo logins
│   │       ├── ApplyScheme.jsx         # Multi-step scheme application form
│   │       ├── ApplicantDashboard.jsx  # Scholar dashboard with renewal & deficiency alerts
│   │       ├── AdminDashboard.jsx      # Scrutiny queue, analytics, notification log, scheme editor
│   │       ├── AdminApplicationDetail.jsx # Deep application inspection with institution sign-off badge
│   │       ├── AdminMeritRanking.jsx   # Interactive formula weight tuning & merit generator
│   │       └── InstitutionDashboard.jsx # University Nodal Officer queue & enrollment verification modal
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.js
├── start_servers.ps1                   # 1-click startup script
└── README.md
```

---

## 🇮🇳 Statutory Compliance & Disclaimer
All fraud risk scores, document classification tags, forensic tampering signals, and algorithmic recommendations generated by this system are advisory indicators provided to assist human desk officers, scrutiny committees, and authorized institutional nodal officers of the Ministry of Tribal Affairs, Government of India. Administrative decisions, candidate selections, and public treasury disbursements strictly comply with official MoTA scheme guidelines and statutory rules.
