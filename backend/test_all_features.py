"""
Comprehensive End-to-End Test Suite for MoTA Scholarship & Fellowship System
Verifies all 5 newly integrated architectural modules:
1. Fraud & Duplicate Detection Engine
2. Document Classifier (wrong-slot detection)
3. Document Quality & Tampering Signals (OpenCV + EXIF)
4. DigiLocker & Aadhaar e-KYC Adapters + PFMS Tracker
5. Immutable Cryptographic Audit Ledger (SHA-256 hash chains)
"""

import unittest
import sys
from datetime import datetime
from app.database import SessionLocal
from app.models import Application, Document, User, AuditLogEntry
from app.fraud_engine import evaluate_application_risk
from app.doc_classifier import classify_document
from app.ocr_engine import analyze_document_quality_and_authenticity
from app.integrations.digilocker import get_sandbox_profiles, fetch_issued_documents
from app.integrations.aadhaar_ekyc import send_aadhaar_otp, verify_aadhaar_otp
from app.integrations.pfms_tracker import get_disbursement_tracker
from app.audit import log_action, verify_chain_integrity, export_audit_trail_json, export_audit_trail_csv

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
        # Test classifier predictions
        res_st = classify_document("Scheduled Tribe Certificate issued by Tehsildar Sub-Divisional Officer Govt of Jharkhand caste Santhal", expected_slot="st_certificate")
        self.assertEqual(res_st["predicted_type"], "st_certificate")
        self.assertGreaterEqual(res_st["confidence"], 0.70)
        
        res_inc = classify_document("Certificate of Gross Annual Family Income from all sources revenue circle officer Rupees 2,40,000", expected_slot="income_certificate")
        self.assertEqual(res_inc["predicted_type"], "income_certificate")
        
        res_adm = classify_document("Office of the Registrar Provisional Admission Offer Letter Doctor of Philosophy Ph.D session 2024-25", expected_slot="income_certificate")
        self.assertEqual(res_adm["predicted_type"], "admission_letter")
        self.assertFalse(res_adm["slot_match"])
        self.assertIsNotNone(res_adm["mismatch_warning"])
        
        # Test seeded wrong-slot application
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
        
        # Test seeded tamper test case
        app_tamper = self.db.query(Application).filter(Application.application_number == "NFST-2026-1006").first()
        doc_tamper = [d for d in app_tamper.documents if d.doc_type == "st_certificate"][0]
        signals = doc_tamper.tampering_signals or {}
        self.assertTrue(signals.get("blur_detected"))
        self.assertTrue(signals.get("moire_screen_photo"))
        self.assertTrue(len(signals.get("tamper_flags", [])) > 0)
        print(f"[OK] Tampering signals detected: Blur={signals.get('blur_severity')}, Flags={signals.get('tamper_flags')}")

    def test_04_digilocker_aadhaar_pfms(self):
        """Priority 4: DigiLocker, Aadhaar e-KYC & PFMS Adapters"""
        print("\n[TEST 4] Testing DigiLocker, Aadhaar e-KYC & PFMS Tracker...")
        # DigiLocker profiles
        profiles = get_sandbox_profiles()
        self.assertGreaterEqual(len(profiles), 3)
        docs_res = fetch_issued_documents("jharkhand_birsa")
        self.assertTrue(docs_res["is_digilocker_verified"])
        self.assertEqual(len(docs_res["documents"]), 3)
        
        # Aadhaar OTP & KYC
        otp_res = send_aadhaar_otp("999911112222")
        self.assertEqual(otp_res["status"], "SUCCESS")
        kyc_res = verify_aadhaar_otp(otp_res["txn_id"], "123456", "999911112222", "Birsa Munda")
        self.assertTrue(kyc_res["is_aadhaar_verified"])
        self.assertEqual(kyc_res["demographics"]["full_name"], "Birsa Munda")
        
        # PFMS Tracker
        pfms_info = get_disbursement_tracker(1, "Selected", "NFST")
        self.assertIn("stages", pfms_info)
        self.assertEqual(len(pfms_info["stages"]), 5)
        print(f"[OK] DigiLocker profiles: {len(profiles)} | Aadhaar KYC: {kyc_res['demographics']['full_name']} | PFMS Stages: {len(pfms_info['stages'])}")

    def test_05_cryptographic_audit_ledger(self):
        """Priority 5: Immutable Cryptographic Audit Trail"""
        print("\n[TEST 5] Testing Cryptographic SHA-256 Audit Trail...")
        # Global chain integrity check
        is_valid, broken_links, blocks = verify_chain_integrity(self.db)
        self.assertTrue(is_valid, f"Broken links: {broken_links}")
        self.assertGreater(len(blocks), 40)
        self.assertEqual(len(broken_links), 0)
        
        # Check specific application ledger export
        app = self.db.query(Application).first()
        dossier = export_audit_trail_json(self.db, app.id)
        self.assertEqual(dossier["mota_audit_dossier"]["application_number"], app.application_number)
        self.assertEqual(dossier["mota_audit_dossier"]["audit_ledger_status"], "INTEGRITY_CERTIFIED")
        
        csv_export = export_audit_trail_csv(self.db, app.id)
        self.assertIn("Block ID", csv_export)
        self.assertIn("Entry Hash (SHA-256)", csv_export)
        print(f"[OK] Verified SHA-256 chain across {len(blocks)} blocks (0 broken links). JSON & CSV RTI dossiers valid.")

if __name__ == "__main__":
    unittest.main()
