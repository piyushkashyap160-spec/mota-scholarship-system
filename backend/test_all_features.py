"""
Comprehensive End-to-End Test Suite for MoTA Scholarship & Fellowship System
Verifies all 10 architectural and feature modules:
1. Fraud & Duplicate Detection Engine
2. Document Classifier (wrong-slot detection)
3. Document Quality & Tampering Signals (OpenCV + EXIF)
4. DigiLocker & Aadhaar e-KYC Adapters + PFMS Tracker
5. Immutable Cryptographic Audit Ledger (SHA-256 hash chains)
6. Real-Time Email & SMS Notification System
7. Admin Scheme Rule Editor
8. Password Reset & OTP Recovery Workflow
9. Multi-Year Fellowship Renewal Workflow
10. Institution Nodal Officer Role & Verification Desk
"""

import unittest
import sys
from datetime import datetime, timedelta
from app.database import SessionLocal
from app.models import Application, Document, User, Scheme, AuditLogEntry, NotificationLog, EnrollmentVerification, PasswordResetToken
from app.fraud_engine import evaluate_application_risk
from app.doc_classifier import classify_document
from app.ocr_engine import analyze_document_quality_and_authenticity
from app.integrations.digilocker import get_sandbox_profiles, fetch_issued_documents
from app.integrations.aadhaar_ekyc import send_aadhaar_otp, verify_aadhaar_otp
from app.integrations.pfms_tracker import get_disbursement_tracker
from app.audit import log_action, verify_chain_integrity, export_audit_trail_json, export_audit_trail_csv
from app.notifications import notification_service
from app.routes.scheme_routes import update_scheme_rules
from app.schemas import SchemeUpdateRequest, ForgotPasswordRequest, ResetPasswordRequest, RenewalSubmitRequest, AdminActionRequest, EnrollmentVerificationRequest
from app.routes.auth_routes import forgot_password, reset_password
from app.routes.application_routes import apply_fellowship_renewal
from app.routes.admin_routes import take_application_action
from app.routes.institution_routes import get_institution_stats, get_institution_applications, verify_institution_enrollment

class TestMotaSystemModules(unittest.TestCase):
    def setUp(self):
        self.db = SessionLocal()

    def tearDown(self):
        self.db.close()

    def test_01_duplicate_and_fraud_engine(self):
        """Priority 1: Duplicate & Fraud Detection Engine"""
        print("\n[TEST 1] Testing Duplicate & Fraud Detection Engine...")
        app_duplicate = self.db.query(Application).filter(Application.application_number == "NFST-2026-1002").first()
        self.assertIsNotNone(app_duplicate)
        
        risk = evaluate_application_risk(app_duplicate, self.db)
        self.assertEqual(risk["risk_level"], "HIGH")
        self.assertGreaterEqual(risk["risk_score"], 70.0)
        
        flag_codes = [f["code"] for f in risk["flags"]]
        self.assertIn("DUPLICATE_ST_CERTIFICATE", flag_codes)
        self.assertIn("SHARED_BANK_ACCOUNT", flag_codes)
        print(f"[OK] Detected {len(risk['flags'])} fraud flags: {flag_codes} (Risk Score: {risk['risk_score']})")

    def test_02_document_classifier(self):
        """Priority 2: Document Classifier (wrong-slot detection)"""
        print("\n[TEST 2] Testing Document Classifier ML Pipeline...")
        res_st = classify_document("Scheduled Tribe Certificate issued by Tehsildar Sub-Divisional Officer Govt of Jharkhand caste Santhal", expected_slot="st_certificate")
        self.assertEqual(res_st["predicted_type"], "st_certificate")
        self.assertGreaterEqual(res_st["confidence"], 0.70)
        
        res_inc = classify_document("Certificate of Gross Annual Family Income from all sources revenue circle officer Rupees 2,40,000", expected_slot="income_certificate")
        self.assertEqual(res_inc["predicted_type"], "income_certificate")
        
        res_adm = classify_document("Office of the Registrar Provisional Admission Offer Letter Doctor of Philosophy Ph.D session 2024-25", expected_slot="income_certificate")
        self.assertEqual(res_adm["predicted_type"], "admission_letter")
        self.assertFalse(res_adm["slot_match"])
        self.assertIsNotNone(res_adm["mismatch_warning"])
        
        app_wrong_slot = self.db.query(Application).filter(Application.application_number == "NFST-2026-1005").first()
        doc_income = [d for d in app_wrong_slot.documents if d.doc_type == "income_certificate"][0]
        self.assertTrue(doc_income.type_mismatch)
        self.assertEqual(doc_income.predicted_type, "admission_letter")
        print(f"[OK] Classified wrong-slot upload correctly: Expected 'income_certificate', Detected '{doc_income.predicted_type}' ({doc_income.classifier_confidence * 100:.0f}%)")

    def test_03_quality_and_tampering_signals(self):
        """Priority 3: Document Quality & Tampering Signals"""
        print("\n[TEST 3] Testing Document Quality & Tampering Signals...")
        analysis = analyze_document_quality_and_authenticity("non_existent_sample.jpg")
        self.assertIn("is_blurry", analysis)
        self.assertIn("disclaimer", analysis)
        self.assertIn("tamper_risk", analysis)
        
        app_tamper = self.db.query(Application).filter(Application.application_number == "TOP_CLASS-2026-1011").first()
        doc_tamper = [d for d in app_tamper.documents if d.doc_type == "st_certificate"][0]
        signals = doc_tamper.tampering_signals or {}
        self.assertTrue(signals.get("blur_detected"))
        self.assertTrue(signals.get("moire_screen_photo"))
        self.assertTrue(len(signals.get("tamper_flags", [])) > 0)
        print(f"[OK] Tampering signals detected: Blur={signals.get('blur_severity')}, Flags={signals.get('tamper_flags')}")

    def test_04_digilocker_aadhaar_pfms(self):
        """Priority 4: DigiLocker, Aadhaar e-KYC & PFMS Adapters"""
        print("\n[TEST 4] Testing DigiLocker, Aadhaar e-KYC & PFMS Tracker...")
        profiles = get_sandbox_profiles()
        self.assertGreaterEqual(len(profiles), 3)
        docs_res = fetch_issued_documents("jharkhand_birsa")
        self.assertTrue(docs_res["is_digilocker_verified"])
        self.assertEqual(len(docs_res["documents"]), 3)
        
        otp_res = send_aadhaar_otp("999911112222")
        self.assertEqual(otp_res["status"], "SUCCESS")
        kyc_res = verify_aadhaar_otp(otp_res["txn_id"], "123456", "999911112222", "Birsa Munda")
        self.assertTrue(kyc_res["is_aadhaar_verified"])
        self.assertEqual(kyc_res["demographics"]["full_name"], "Birsa Munda")
        
        pfms_info = get_disbursement_tracker(1, "Selected", "NFST")
        self.assertIn("stages", pfms_info)
        self.assertEqual(len(pfms_info["stages"]), 5)
        print(f"[OK] DigiLocker profiles: {len(profiles)} | Aadhaar KYC: {kyc_res['demographics']['full_name']} | PFMS Stages: {len(pfms_info['stages'])}")

    def test_05_cryptographic_audit_ledger(self):
        """Priority 5: Immutable Cryptographic Audit Trail"""
        print("\n[TEST 5] Testing Cryptographic SHA-256 Audit Trail...")
        is_valid, broken_links, blocks = verify_chain_integrity(self.db)
        self.assertTrue(is_valid, f"Broken links: {broken_links}")
        self.assertGreater(len(blocks), 40)
        self.assertEqual(len(broken_links), 0)
        
        app = self.db.query(Application).first()
        dossier = export_audit_trail_json(self.db, app.id)
        self.assertEqual(dossier["mota_audit_dossier"]["application_number"], app.application_number)
        self.assertEqual(dossier["mota_audit_dossier"]["audit_ledger_status"], "INTEGRITY_CERTIFIED")
        
        csv_export = export_audit_trail_csv(self.db, app.id)
        self.assertIn("Block ID", csv_export)
        self.assertIn("Entry Hash (SHA-256)", csv_export)
        print(f"[OK] Verified SHA-256 chain across {len(blocks)} blocks (0 broken links). JSON & CSV RTI dossiers valid.")

    def test_06_email_and_sms_notifications(self):
        """Feature 1: Real-Time Email & SMS Notification System"""
        print("\n[TEST 6] Testing Email & SMS Notification Service...")
        sent_mail = notification_service.send_email(
            to_email="test.scholar@tribal.gov.in",
            subject="Test Notification Verification",
            body_html="<p>Test notification body.</p>"
        )
        self.assertTrue(sent_mail)

        sent_sms = notification_service.send_sms_stub(
            phone="+91-98765-43210",
            message="MoTA Test SMS alert"
        )
        self.assertTrue(sent_sms)

        logs = self.db.query(NotificationLog).all()
        self.assertGreater(len(logs), 0)
        print(f"[OK] Notifications verified. Recorded {len(logs)} dispatch entries in database ledger.")

    def test_07_scheme_rule_editor(self):
        """Feature 2: Admin Scheme Rule Editor"""
        print("\n[TEST 7] Testing Admin Scheme Rule Editor...")
        admin = self.db.query(User).filter(User.role == "admin").first()
        update_req = SchemeUpdateRequest(
            income_ceiling=650000.0,
            min_marks=55.0,
            objective="Updated statutory objective for ST fellowship excellence."
        )
        updated = update_scheme_rules("NFST", update_req, current_admin=admin, db=self.db)
        self.assertEqual(updated.income_ceiling, 650000.0)

        # Verify audit log entry created for rule change
        rule_logs = self.db.query(AuditLogEntry).filter(AuditLogEntry.action == "Scheme Rule Updated").all()
        self.assertGreater(len(rule_logs), 0)
        print(f"[OK] Scheme rule editor updated threshold to Rs. 6,50,000 and logged to cryptographic audit ledger.")


    def test_08_password_reset_flow(self):
        """Feature 3: Password Reset & OTP Recovery"""
        print("\n[TEST 8] Testing Password Reset & OTP Flow...")
        forgot_res = forgot_password(ForgotPasswordRequest(email="birsa.soren@research.ac.in"), db=self.db)
        self.assertIn("OTP", forgot_res["message"])

        token_record = self.db.query(PasswordResetToken).filter(
            PasswordResetToken.used == False
        ).order_by(PasswordResetToken.id.desc()).first()
        self.assertIsNotNone(token_record)

        reset_res = reset_password(ResetPasswordRequest(
            email="birsa.soren@research.ac.in",
            otp=token_record.token,
            new_password="scholar_new_password_123"
        ), db=self.db)
        self.assertIn("success", reset_res["message"].lower())

        # Restore password for ongoing test consistency
        from app.auth import get_password_hash
        birsa = self.db.query(User).filter(User.email == "birsa.soren@research.ac.in").first()
        birsa.hashed_password = get_password_hash("scholar123")
        self.db.commit()
        print("[OK] Password reset OTP generated, validated, and user credentials successfully updated.")

    def test_09_fellowship_renewal_flow(self):
        """Feature 4: Multi-Year Fellowship Renewal Workflow"""
        print("\n[TEST 9] Testing Fellowship Renewal Continuation Flow...")
        applicant = self.db.query(User).filter(User.email == "birsa.soren@research.ac.in").first()
        admin = self.db.query(User).filter(User.role == "admin").first()
        parent_app = self.db.query(Application).filter(Application.user_id == applicant.id, Application.status == "Selected").first()
        self.assertIsNotNone(parent_app)

        # Clean existing pending renewals for testing
        self.db.query(Application).filter(Application.parent_application_id == parent_app.id).delete()
        self.db.commit()

        initial_due_date = parent_app.renewal_due_date

        req = RenewalSubmitRequest(
            progress_report="Satisfactory completion of Year 1 doctoral coursework and field ethnography.",
            continuation_institution="Central University of Jharkhand",
            continuation_course="Ph.D. Tribal Studies",
            bank_account_confirmed=True,
            current_year_semester="Year 2 (Semester 3-4)",
            supervisor_guide_name="Dr. Ramesh Murmu",
            marks_or_grade="A+ Grade"
        )
        renewal = apply_fellowship_renewal(parent_app.id, req, current_user=applicant, db=self.db)
        self.assertEqual(renewal.status, "Renewal - Under Review")
        self.assertEqual(renewal.parent_application_id, parent_app.id)

        # Admin approves renewal
        admin_act = AdminActionRequest(action="approve", stage="Renewal", remarks="Annual progress confirmed satisfactory.")
        res = take_application_action(renewal.id, admin_act, current_admin=admin, db=self.db)
        self.assertEqual(res["current_status"], "Selected")

        self.db.refresh(parent_app)
        self.assertNotEqual(parent_app.renewal_due_date, initial_due_date)
        print(f"[OK] Fellowship renewal created linked application and extended award validity to: {parent_app.renewal_due_date}")

    def test_10_institution_nodal_verification(self):
        """Feature 5: Institution Nodal Officer Role & Verification"""
        print("\n[TEST 10] Testing Institution Nodal Officer Workflow...")
        nodal = self.db.query(User).filter(User.email == "nodal@cuj.ac.in").first()
        self.assertIsNotNone(nodal)
        self.assertEqual(nodal.role, "institution")

        stats = get_institution_stats(current_officer=nodal, db=self.db)
        self.assertGreater(stats["total_applications"], 0)

        apps = get_institution_applications(current_officer=nodal, db=self.db)
        self.assertGreater(len(apps), 0)

        target_app = apps[0]
        verif_res = verify_institution_enrollment(
            app_id=target_app.id,
            payload=EnrollmentVerificationRequest(
                enrolled=True,
                enrollment_number="CUJ/PHD/ST/2026/001",
                remarks="Full-time enrolled regular doctoral student verified."
            ),
            current_officer=nodal,
            db=self.db
        )
        self.assertTrue(verif_res["enrollment_verified"])
        print(f"[OK] Institution Nodal Desk verified: {stats['institution_name']} ({stats['total_applications']} scholars scoped).")

if __name__ == "__main__":
    unittest.main()
