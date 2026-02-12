import sqlite3
import hashlib
import json
import time
from typing import Dict, Any

DB_PATH = "vetos_audit_ledger.db"

class AuditLedger:
    def __init__(self, db_path: str = DB_PATH):
        self.conn = sqlite3.connect(db_path)
        self._init_schema()

    def _init_schema(self):
        """Initialize the immutable ledger table with hash chaining."""
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                actor_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                payload TEXT NOT NULL,
                prev_hash TEXT NOT NULL,
                curr_hash TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def _get_last_hash(self) -> str:
        """Fetch the hash of the most recent entry to maintain the chain."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT curr_hash FROM audit_log ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        return row[0] if row else "0" * 64  # Genesis hash

    def _compute_hash(self, timestamp: float, actor_id: str, event_type: str, payload: str, prev_hash: str) -> str:
        """SHA-256 hash of the entire row content + previous hash."""
        content = f"{timestamp}{actor_id}{event_type}{payload}{prev_hash}"
        return hashlib.sha256(content.encode()).hexdigest()

    def log_event(self, actor_id: str, event_type: str, payload: Dict[str, Any]):
        """
        Writes an event to the ledger. 
        This is an ACID transaction that enforces the hash chain.
        """
        payload_str = json.dumps(payload, sort_keys=True)
        timestamp = time.time()
        
        with self.conn: # Auto-commit block
            prev_hash = self._get_last_hash()
            curr_hash = self._compute_hash(timestamp, actor_id, event_type, payload_str, prev_hash)
            
            self.conn.execute("""
                INSERT INTO audit_log (timestamp, actor_id, event_type, payload, prev_hash, curr_hash)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (timestamp, actor_id, event_type, payload_str, prev_hash, curr_hash))
            
        print(f"[AUDIT] Event Logged: {curr_hash[:8]}... (Linked to: {prev_hash[:8]}...)")

    def verify_integrity(self) -> bool:
        """
        Replays the entire ledger to verify the cryptographic chain.
        Returns True if the ledger is untampered.
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT timestamp, actor_id, event_type, payload, prev_hash, curr_hash FROM audit_log ORDER BY id ASC")
        rows = cursor.fetchall()
        
        expected_prev = "0" * 64
        for row in rows:
            ts, actor, evt, load, p_hash, c_hash = row
            
            # Check 1: Does the previous hash match the chain?
            if p_hash != expected_prev:
                print(f"[ALERT] Broken Chain at Event {evt}! Expected {expected_prev[:8]}, got {p_hash[:8]}")
                return False
            
            # Check 2: Is the current hash valid?
            recalc_hash = self._compute_hash(ts, actor, evt, load, p_hash)
            if recalc_hash != c_hash:
                print(f"[ALERT] Tampering Detected at Event {evt}! Data does not match hash.")
                return False
                
            expected_prev = c_hash
            
        print("[AUDIT] Integrity Check Passed: Ledger is valid.")
        return True

# --- Quick Test ---
if __name__ == "__main__":
    ledger = AuditLedger()
    
    # 1. Log some events
    ledger.log_event("SYSTEM_01", "INIT_SEQUENCE", {"status": "OK", "version": "2.0.1"})
    ledger.log_event("USER_ADMIN", "CONFIG_CHANGE", {"param": "MAX_RETRIES", "val": 5})
    
    # 2. Verify Chain
    ledger.verify_integrity()
