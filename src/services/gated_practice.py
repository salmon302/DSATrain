"""
GatedPractice: Manage problem gates (dry-run → pseudocode → code).

Persistence strategy:
- If a SQLAlchemy Session is provided and the practice_gate_sessions table exists, use DB.
- Otherwise, fall back to a simple JSON store on disk for local sessions.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import inspect

try:
    # Lazy import to avoid circulars when used outside app context
    from src.models.database import PracticeGateSession
except Exception:
    PracticeGateSession = None  # type: ignore

DEFAULT_STORE = Path("config/practice_sessions.json")


class GatedPractice:
    def __init__(self, store_path: Optional[Path] = None, db: Optional[Session] = None, user_id: str = "default_user"):
        # Bind default at runtime so tests can monkeypatch DEFAULT_STORE
        self.store_path = store_path or DEFAULT_STORE
        self.db = db
        self.user_id = user_id or "default_user"
        # Prepare JSON store directory
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.store_path.exists():
            self._write({})

    def _read(self) -> Dict[str, Any]:
        try:
            return json.loads(self.store_path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _write(self, data: Dict[str, Any]):
        self.store_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def _db_available(self) -> bool:
        if self.db is None or PracticeGateSession is None:
            return False
        try:
            inspector = inspect(self.db.bind)
            return inspector.has_table("practice_gate_sessions")
        except Exception:
            return False

    def start(self, problem_id: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        key = session_id or f"sess_{problem_id}"
        if self._db_available():
            # Upsert-like behavior: find existing by session_id
            sess = self.db.query(PracticeGateSession).filter(PracticeGateSession.session_id == key).first()
            if not sess:
                sess = PracticeGateSession(
                    session_id=key,
                    user_id=self.user_id,
                    problem_id=problem_id,
                    gates={"dry_run": False, "pseudocode": False, "code": False},
                    unlocked=False,
                )
                self.db.add(sess)
            else:
                # Reset gates if restarting
                sess.gates = {"dry_run": False, "pseudocode": False, "code": False}
                sess.unlocked = False
                sess.problem_id = problem_id
                sess.user_id = self.user_id
            self.db.commit()
            self.db.refresh(sess)
            return {
                "session_id": sess.session_id,
                "problem_id": sess.problem_id,
                "gates": sess.gates,
                "unlocked": bool(sess.unlocked),
                "started_at": (sess.started_at.isoformat() if getattr(sess, "started_at", None) else datetime.now().isoformat()),
            }
        # JSON fallback
        data = self._read()
        data[key] = {
            "problem_id": problem_id,
            "gates": {"dry_run": False, "pseudocode": False, "code": False},
            "unlocked": False,
            "started_at": datetime.now().isoformat(),
        }
        self._write(data)
        return {"session_id": key, **data[key]}

    def progress(self, session_id: str, gate: str, value: bool = True) -> Dict[str, Any]:
        if gate not in {"dry_run", "pseudocode", "code"}:
            raise ValueError("Invalid gate")
        if self._db_available():
            sess = self.db.query(PracticeGateSession).filter(PracticeGateSession.session_id == session_id).first()
            if not sess:
                raise KeyError("Session not found")
            gates = dict(sess.gates or {"dry_run": False, "pseudocode": False, "code": False})
            gates[gate] = bool(value)
            # Preserve original unlock logic (unlock if all gates true OR when code gate is touched)
            unlocked = (all(gates.get(k) for k in ["dry_run", "pseudocode", "code"]) or gate == "code")
            sess.gates = gates
            sess.unlocked = bool(unlocked)
            self.db.commit()
            self.db.refresh(sess)
            return {
                "session_id": sess.session_id,
                "problem_id": sess.problem_id,
                "gates": sess.gates,
                "unlocked": bool(sess.unlocked),
                "started_at": (sess.started_at.isoformat() if getattr(sess, "started_at", None) else datetime.now().isoformat()),
            }
        # JSON fallback
        data = self._read()
        sess = data.get(session_id)
        if not sess:
            raise KeyError("Session not found")
        sess["gates"][gate] = bool(value)
        sess["unlocked"] = all(sess["gates"].get(k) for k in ["dry_run", "pseudocode", "code"]) or gate == "code"
        data[session_id] = sess
        self._write(data)
        return {"session_id": session_id, **sess}

    def status(self, session_id: str) -> Dict[str, Any]:
        if self._db_available():
            sess = self.db.query(PracticeGateSession).filter(PracticeGateSession.session_id == session_id).first()
            if not sess:
                raise KeyError("Session not found")
            return {
                "session_id": sess.session_id,
                "problem_id": sess.problem_id,
                "gates": sess.gates,
                "unlocked": bool(sess.unlocked),
                "started_at": (sess.started_at.isoformat() if getattr(sess, "started_at", None) else datetime.now().isoformat()),
            }
        data = self._read()
        sess = data.get(session_id)
        if not sess:
            raise KeyError("Session not found")
        return {"session_id": session_id, **sess}

    # ---- Management helpers ----
    def list(self, problem_id: Optional[str] = None, limit: int = 100) -> list[Dict[str, Any]]:
        if self._db_available():
            q = self.db.query(PracticeGateSession)
            if problem_id:
                q = q.filter(PracticeGateSession.problem_id == problem_id)
            rows = q.order_by(PracticeGateSession.started_at.desc()).limit(limit).all()
            return [
                {
                    "session_id": r.session_id,
                    "user_id": r.user_id,
                    "problem_id": r.problem_id,
                    "gates": r.gates,
                    "unlocked": bool(r.unlocked),
                    "started_at": (r.started_at.isoformat() if r.started_at else None),
                    "updated_at": (r.updated_at.isoformat() if r.updated_at else None),
                }
                for r in rows
            ]
        data = self._read()
        items = []
        for sid, sess in data.items():
            if problem_id and sess.get("problem_id") != problem_id:
                continue
            items.append({"session_id": sid, **sess})
        # Sort by started_at desc if present
        items.sort(key=lambda x: x.get("started_at") or "", reverse=True)
        return items[:limit]

    def get(self, session_id: str) -> Dict[str, Any]:
        return self.status(session_id)

    def delete(self, session_id: str) -> Dict[str, Any]:
        if self._db_available():
            sess = self.db.query(PracticeGateSession).filter(PracticeGateSession.session_id == session_id).first()
            if not sess:
                raise KeyError("Session not found")
            self.db.delete(sess)
            self.db.commit()
            return {"deleted": True, "session_id": session_id}
        data = self._read()
        if session_id not in data:
            raise KeyError("Session not found")
        data.pop(session_id, None)
        self._write(data)
        return {"deleted": True, "session_id": session_id}
