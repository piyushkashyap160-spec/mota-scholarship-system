"""
MoTA Cryptographic Audit Ledger Engine (Priority 5)
Provides an append-only, SHA-256 hash-chained immutable audit trail for every
state transition, officer action, AI document scan, and disbursement event.
Supports real-time mathematical integrity verification and RTI-ready audit export.
"""

import hashlib
import io
import csv
from datetime import datetime
from typing import Dict, Any, List, Tuple, Optional
from sqlalchemy.orm import Session
from .models import AuditLogEntry, Application

GENESIS_HASH = "0" * 64

def compute_entry_hash(
    previous_hash: str,
    timestamp_iso: str,
    actor_name: str,
    action: str,
    previous_state: str,
    new_state: str,
    remarks: str
) -> str:
    """Computes deterministic SHA-256 hash for an audit ledger block."""
    payload = f"{previous_hash}|{timestamp_iso}|{actor_name}|{action}|{previous_state}|{new_state}|{remarks}"
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()

def log_action(
    db: Session,
    application_id: int,
    actor_name: str,
    actor_role: str,
    action: str,
    previous_state: Optional[str] = None,
    new_state: Optional[str] = None,
    remarks: Optional[str] = "",
    stage: Optional[str] = None,
    document_id: Optional[int] = None,
    details: Optional[Dict[str, Any]] = None,
    user_id: Optional[int] = None
) -> AuditLogEntry:
    """
    Appends a new cryptographically chained audit log entry to the application's ledger.
    """
    # Find latest entry to get previous block hash
    last_entry = db.query(AuditLogEntry)\
        .filter(AuditLogEntry.application_id == application_id)\
        .order_by(AuditLogEntry.id.desc())\
        .first()

    previous_hash = last_entry.entry_hash if last_entry else GENESIS_HASH
    created_at = datetime.utcnow()
    created_iso = created_at.isoformat()

    entry_hash = compute_entry_hash(
        previous_hash=previous_hash,
        timestamp_iso=created_iso,
        actor_name=actor_name,
        action=action,
        previous_state=previous_state or "",
        new_state=new_state or "",
        remarks=remarks or ""
    )

    entry = AuditLogEntry(
        application_id=application_id,
        user_id=user_id,
        actor_name=actor_name,
        actor_role=actor_role,
        action=action,
        previous_state=previous_state,
        new_state=new_state,
        stage=stage or new_state or "General",
        remarks=remarks,
        document_id=document_id,
        details=details or {},
        previous_hash=previous_hash,
        entry_hash=entry_hash,
        created_at=created_at
    )

    db.add(entry)
    db.flush()
    return entry

def verify_chain_integrity(db: Session, application_id: Optional[int] = None) -> Tuple[bool, List[str], List[Dict[str, Any]]]:
    """
    Cryptographic verification:
    Walks the chain from Genesis block, re-computing each block's SHA-256 hash.
    If application_id is provided, verifies that application's ledger.
    If application_id is None, verifies ledgers across all applications.
    Returns: (is_valid: bool, broken_links: List[str], blocks: List[dict])
    """
    if application_id is not None:
        target_app_ids = [application_id]
    else:
        rows = db.query(AuditLogEntry.application_id).distinct().all()
        target_app_ids = [r[0] for r in rows]

    if not target_app_ids:
        return True, ["Genesis state: Ledger empty."], []

    all_broken_links = []
    all_blocks = []

    for app_id in target_app_ids:
        entries = db.query(AuditLogEntry)\
            .filter(AuditLogEntry.application_id == app_id)\
            .order_by(AuditLogEntry.id.asc())\
            .all()

        expected_prev = GENESIS_HASH
        for entry in entries:
            # 1. Check previous_hash link
            link_valid = (entry.previous_hash == expected_prev)
            if not link_valid:
                all_broken_links.append(
                    f"Broken Link at App #{app_id} Block #{entry.id}: previous_hash ({entry.previous_hash[:12]}...) "
                    f"does not match expected ({expected_prev[:12]}...)"
                )

            # 2. Re-compute block hash
            recalculated_hash = compute_entry_hash(
                previous_hash=entry.previous_hash,
                timestamp_iso=entry.created_at.isoformat(),
                actor_name=entry.actor_name,
                action=entry.action,
                previous_state=entry.previous_state or "",
                new_state=entry.new_state or "",
                remarks=entry.remarks or ""
            )

            hash_intact = (recalculated_hash == entry.entry_hash)
            if not hash_intact:
                all_broken_links.append(
                    f"Tamper Detected at App #{app_id} Block #{entry.id}: entry_hash altered! "
                    f"Stored: {entry.entry_hash[:12]}..., Recalculated: {recalculated_hash[:12]}..."
                )

            block_dict = {
                "block_id": entry.id,
                "application_id": entry.application_id,
                "timestamp": entry.created_at.isoformat(),
                "actor": f"{entry.actor_name} ({entry.actor_role})",
                "action": entry.action,
                "transition": f"{entry.previous_state or 'None'} ➔ {entry.new_state or 'None'}",
                "remarks": entry.remarks,
                "previous_hash": entry.previous_hash,
                "entry_hash": entry.entry_hash,
                "is_valid": link_valid and hash_intact
            }
            all_blocks.append(block_dict)
            expected_prev = entry.entry_hash

    is_chain_valid = len(all_broken_links) == 0
    return is_chain_valid, all_broken_links, all_blocks

def export_audit_trail_json(db: Session, application_id: int) -> Dict[str, Any]:
    """Generates official RTI (Right to Information) compliance audit dossier in JSON format."""
    app = db.query(Application).filter(Application.id == application_id).first()
    is_valid, broken_links, blocks = verify_chain_integrity(db, application_id)

    return {
        "mota_audit_dossier": {
            "application_number": app.application_number if app else f"APP-{application_id}",
            "scheme": app.scheme.name if app and app.scheme else "MoTA Fellowship",
            "applicant_name": app.applicant.full_name if app and app.applicant else "ST Candidate",
            "audit_ledger_status": "INTEGRITY_CERTIFIED" if is_valid else "TAMPER_DETECTED",
            "cryptographic_algorithm": "SHA-256 Genesis Hash Chain",
            "total_audit_blocks": len(blocks),
            "generated_at": datetime.utcnow().isoformat(),
            "broken_links": broken_links,
            "ledger_blocks": blocks
        }
    }

def export_audit_trail_csv(db: Session, application_id: int) -> str:
    """Generates RFC 4180 CSV export of the cryptographic audit ledger."""
    is_valid, broken_links, blocks = verify_chain_integrity(db, application_id)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Block ID", "Timestamp", "Actor", "Action", "State Transition", "Remarks", "Entry Hash (SHA-256)", "Previous Hash (SHA-256)", "Integrity"])

    for b in blocks:
        writer.writerow([
            b["block_id"],
            b["timestamp"],
            b["actor"],
            b["action"],
            b["transition"],
            b["remarks"],
            b["entry_hash"],
            b["previous_hash"],
            "VALID" if b["is_valid"] else "CORRUPTED"
        ])

    return output.getvalue()
