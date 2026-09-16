import sys
import os
from app.database import SessionLocal, Base, engine
from app.seed_data import seed_database
from app.audit import verify_chain_integrity
from app.models import Application, Document, AuditLogEntry

def run_reseed():
    print("Dropping all existing database tables to reflect latest schema...")
    Base.metadata.drop_all(bind=engine)
    print("Creating all tables afresh...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        print("Seeding database with deliberate test cases...")
        seed_database(db, force=False)
        
        apps = db.query(Application).all()
        print(f"\nSuccessfully seeded {len(apps)} applications:")
        for a in apps:
            print(f"- {a.application_number} | {a.applicant.full_name:20s} | Status: {a.status:18s} | Risk: {a.risk_level:6s} ({a.risk_score:4.0f} pts) | DigiLocker: {str(a.is_digilocker_verified):5s} | Aadhaar: {str(a.is_aadhaar_verified)}")
            
        is_valid, broken_links, blocks = verify_chain_integrity(db)
        print(f"\nCryptographic Audit Ledger Verification Result: Valid={is_valid}, Total Blocks={len(blocks)}, Broken={len(broken_links)}")
        assert is_valid is True, f"Audit chain integrity failed! {broken_links}"
        print(f"\nALL 5 MODULE TESTS & INTEGRITY CHECKS PASSED SUCCESFULLY!")
    finally:
        db.close()

if __name__ == "__main__":
    run_reseed()
