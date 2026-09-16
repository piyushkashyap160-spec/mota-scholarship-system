# MoTA Scholarship & Fellowship Management System
### Ministry of Tribal Affairs (MoTA) | Smart India Hackathon (SIH) Problem Statement 26239

A comprehensive, end-to-end digital platform designed for Scheduled Tribe (ST) students across India. It modernizes fellowship management from registration to post-selection DBT tracking, featuring **schema-driven scheme configurability**, **AI-assisted Tesseract OCR document verification with side-by-side discrepancy matrices**, and **assistive merit ranking** for administrative scrutiny committees.

---

## 🏛️ Core Features

1. **True Scheme Configurability (Core SIH Requirement)**:
   - **NFST** (*National Fellowship for STs in India*) & **NOS** (*National Overseas Scholarship Abroad*) are defined completely through backend JSON rulebases.
   - Dynamic parameters: required documents, eligibility rules (income ceiling, qualifying cut-off marks, degree levels), and form fields.
   - Generic Dynamic Form Renderer on frontend automatically generates forms from scheme specifications.
   - Admin Scheme Rule Inspector displays both visual specification cards and raw JSON schemas.

2. **AI-Assisted Document Intelligence & Cross-Verification ("Wow" Moment)**:
   - Tesseract OCR extracts key data from uploaded certificates (ST caste certificate, annual income certificate, university admission letter, mark sheets).
   - Live discrepancy detection comparing applicant-entered values against OCR-extracted fields with fuzzy matching.
   - Per-document verification statuses: `Verified` (green), `Needs Review` (amber mismatch highlight), and `Missing/Unreadable` (red).

3. **Applicant Portal & Lifecycle Tracking**:
   - Dynamic multi-step application wizard with real-time OCR feedback.
   - 5-stage Application Status Timeline:
     `Submitted` $\rightarrow$ `Under AI Verification` $\rightarrow$ `Scrutiny` $\rightarrow$ `Selected / Rejected` $\rightarrow$ `Post-Selection (DBT Disbursement)`.
   - **Deficiency Action Center**: Instant alerts if a document is flagged by an officer, with a 1-click **Resubmit Document** workflow.

4. **Admin Portal & Scrutiny Panel**:
   - Master scrutiny table with multi-filters (Scheme, Verification Status, Domicile State, Search Query).
   - Side-by-Side Scrutiny Workspace: Document viewer with OCR chips, discrepancy highlighting, and automated rule check results.
   - Administrative actions: Approve, Reject, or Request Resubmission (raises deficiency).
   - **Assistive Merit Ranking Table**: Configurable weights (Academic Marks vs. Economic Need) supporting "AI assists, human decides" governance.
   - Analytics Dashboard: Live metrics, status distribution, state demographics, velocity, and top flagged documents.

5. **Government of India Aesthetic**:
   - Official Indian Tricolor ribbon banner (`#FF9933`, `#FFFFFF`, `#138808`), MoTA Deep Blue (`#0B3B60`), accessible typography, and printable records.

---

## 🚀 Quickstart & Setup Guide

### Prerequisites
- Node.js (v18+) & npm
- Python (v3.10 - 3.12 recommended)

### 1-Click Launch (Windows PowerShell)
From the root directory:
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

#### Terminal 2 — Frontend (React + Vite):
```powershell
cd frontend
npm run dev
```
- Frontend Portal URL: `http://127.0.0.1:5173`

---

## 🔑 Pre-Seeded Demo Accounts (Instant 1-Click Access)

The platform comes pre-seeded with **2 schemes** and **18 realistic ST applicant profiles** spanning diverse states (Jharkhand, Odisha, MP, Assam, Meghalaya, etc.) and communities (Santhal, Gond, Bhil, Munda, Khasi):

| Role | Name | Email | Password | Demo Scenario |
| :--- | :--- | :--- | :--- | :--- |
| **Admin** | Dr. R. K. Soren, IAS (MoTA) | `admin@mota.gov.in` | `admin123` | Master scrutiny table, merit ranking, analytics |
| **Applicant** | Birsa Soren | `birsa.soren@research.ac.in` | `scholar123` | **Selected Scholar** with active DBT fellowship |
| **Applicant** | Sanjay Marandi | `sanjay.marandi@stmail.in` | `scholar123` | **Needs Review** with open deficiency to resubmit |
| **Applicant** | Sunil Kharwar | `sunil.kharwar@stmail.in` | `scholar123` | **Submitted** application under initial queue |

> **Tip for Judges**: You can also use the **"Demo View"** button in the top navigation bar to seamlessly toggle between Admin Scrutiny and Applicant views in 1 click!

---

## 📂 Project Architecture

```
mota-scholarship-system/
├── backend/
│   ├── app/
│   │   ├── main.py                     # FastAPI entrypoint, CORS, startup seed
│   │   ├── config.py                   # App configuration & paths
│   │   ├── database.py                 # SQLite / PostgreSQL engine
│   │   ├── models.py                   # SQLAlchemy ORM models
│   │   ├── schemas.py                  # Pydantic v2 schemas
│   │   ├── auth.py                     # JWT token & bcrypt hashing
│   │   ├── ocr_engine.py               # Tesseract OCR & Document Intelligence
│   │   ├── eligibility_engine.py       # JSON rulebase qualification engine
│   │   ├── merit_engine.py             # Assistive scoring & ranking algorithm
│   │   ├── seed_data.py                # Pre-seeded schemes & 18 applicant profiles
│   │   └── routes/                     # API routers (auth, schemes, docs, apps, admin)
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/client.js               # API service layer
│   │   ├── components/                 # Navbar, StatusBadge, DynamicFormRenderer,
│   │   │                               # DocumentUploader, SideBySideOcrViewer, Timeline
│   │   └── pages/                      # Home, Login, ApplyScheme, ApplicantDashboard,
│   │                                   # AdminDashboard, AdminApplicationDetail, AdminMeritRanking
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.js
├── start_servers.ps1                   # 1-click startup script
└── README.md
```
