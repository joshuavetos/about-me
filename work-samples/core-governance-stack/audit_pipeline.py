import sqlite3
import json
import time

class AuditLedger:
    def __init__(self, db_path: str = "vetos_audit_ledger.db"):
        self.conn = sqlite3.connect(db_path)
        self._init_schema()

    def _init_schema(self):
        """Initializes the scalar-ready audit ledger."""
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                event_type TEXT,
                risk_weight REAL,
                reasoning_metadata TEXT
            )
        """)
        self.conn.commit()

    def log_scaling_event(self, risk_weight: float, metadata: dict):
        """Logs a proportional scaling decision with architectural reasoning."""
        with self.conn:
            self.conn.execute("""
                INSERT INTO audit_log (timestamp, event_type, risk_weight, reasoning_metadata)
                VALUES (?, ?, ?, ?)
            """, (time.time(), "RISK_SCALING", risk_weight, json.dumps(metadata)))
        print(f"[AUDIT] Scaling Event Logged: {risk_weight*100:.1f}% Exposure allocated.")

    def get_latest_audit(self):
        """Retrieves the last logged system state for verification."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM audit_log ORDER BY id DESC LIMIT 1")
        return cursor.fetchone()

if __name__ == "__main__":
    ledger = AuditLedger()
    # Mock scaling event for structural verification
    ledger.log_scaling_event(0.421, {"reason": "Volatility Expansion", "trap_active": False})
