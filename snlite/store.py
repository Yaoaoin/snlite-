from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
from uuid import uuid4

@dataclass
class Session:
    id: str
    title: str
    created_at: float
    updated_at: float
    messages: List[Dict[str, Any]]  # {role, content}

class SessionStore:
    """
    Lightweight JSONL store:
    - file: data/sessions.jsonl
    - each line is a full session snapshot
    - last snapshot wins
    """
    def __init__(self, data_dir: str) -> None:
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        self.path = os.path.join(self.data_dir, "sessions.jsonl")

    def _load_all_snapshots(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.path):
            return []
        out: List[Dict[str, Any]] = []
        with open(self.path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    out.append(json.loads(line))
                except Exception:
                    continue
        return out

    def _materialize(self) -> Dict[str, Session]:
        snapshots = self._load_all_snapshots()
        by_id: Dict[str, Session] = {}
        for s in snapshots:
            try:
                sess = Session(
                    id=s["id"],
                    title=s.get("title", "Untitled"),
                    created_at=float(s.get("created_at", time.time())),
                    updated_at=float(s.get("updated_at", time.time())),
                    messages=list(s.get("messages", [])),
                )
                by_id[sess.id] = sess
            except Exception:
                continue
        return by_id

    def list_sessions(self) -> List[Dict[str, Any]]:
        by_id = self._materialize()
        items = sorted(by_id.values(), key=lambda x: x.updated_at, reverse=True)
        return [{"id": s.id, "title": s.title, "updated_at": s.updated_at, "created_at": s.created_at} for s in items]

    def get_session(self, session_id: str) -> Optional[Session]:
        by_id = self._materialize()
        return by_id.get(session_id)

    def create_session(self, title: str = "New Chat") -> Session:
        now = time.time()
        sess = Session(
            id=uuid4().hex,
            title=title,
            created_at=now,
            updated_at=now,
            messages=[],
        )
        self.save_session(sess)
        return sess

    def save_session(self, session: Session) -> None:
        session.updated_at = time.time()
        line = json.dumps(asdict(session), ensure_ascii=False)
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(line + "\n")

    def rename_session(self, session_id: str, title: str) -> Optional[Session]:
        sess = self.get_session(session_id)
        if not sess:
            return None
        sess.title = title
        self.save_session(sess)
        return sess

    def delete_session(self, session_id: str) -> bool:
        """
        JSONL "delete" by writing a tombstone snapshot with messages empty + special flag.
        Materialize will keep last snapshot; we treat deleted sessions as absent.
        """
        sess = self.get_session(session_id)
        if not sess:
            return False
        now = time.time()
        tomb = {
            "id": session_id,
            "title": "__deleted__",
            "created_at": sess.created_at,
            "updated_at": now,
            "messages": [],
            "deleted": True,
        }
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(tomb, ensure_ascii=False) + "\n")
        return True

    def export_markdown(self, session_id: str) -> Optional[str]:
        sess = self.get_session(session_id)
        if not sess:
            return None
        # If deleted
        if sess.title == "__deleted__":
            return None
        lines = [f"# {sess.title}", ""]
        for m in sess.messages:
            role = m.get("role", "")
            content = m.get("content", "")
            if role == "user":
                lines.append(f"## User\n\n{content}\n")
            elif role == "assistant":
                lines.append(f"## Assistant\n\n{content}\n")
            elif role == "system":
                lines.append(f"## System\n\n{content}\n")
            else:
                lines.append(f"## {role}\n\n{content}\n")
        return "\n".join(lines)