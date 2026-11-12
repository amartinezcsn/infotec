from __future__ import annotations

import json
import re
from pathlib import Path

from ..settings import POLICY_DIR


UNTRUSTED_INSTRUCTION_PATTERNS = (
    re.compile(r"ignore\s+(all\s+)?previous", re.I),
    re.compile(r"system\s+prompt", re.I),
    re.compile(r"<\s*admin", re.I),
    re.compile(r"execute\s+(this\s+)?command", re.I),
)


def _safe_text(text: str) -> str:
    lines = []
    for line in text.splitlines():
        if any(pattern.search(line) for pattern in UNTRUSTED_INSTRUCTION_PATTERNS):
            continue
        lines.append(line)
    return "\n".join(lines).strip()


def search_delivery_knowledge(query: str, policy_dir: Path | None = None, limit: int = 3) -> dict:
    directory = policy_dir or POLICY_DIR
    terms = {token for token in re.findall(r"[a-záéíóúñ0-9]+", query.lower()) if len(token) > 2}
    matches = []
    for path in sorted(directory.glob("*.json")):
        document = json.loads(path.read_text(encoding="utf-8"))
        if document.get("status") != "approved":
            continue
        for section in document.get("sections", []):
            safe_content = _safe_text(section.get("content", ""))
            haystack = f"{section.get('title', '')} {safe_content}".lower()
            score = sum(1 for term in terms if term in haystack)
            if score:
                matches.append({
                    "score": score,
                    "content": safe_content,
                    "citation": {
                        "document_id": document["document_id"],
                        "title": document["title"],
                        "section": section["title"],
                        "version": document["version"],
                        "status": document["status"],
                    },
                })
    matches.sort(key=lambda item: item["score"], reverse=True)
    selected = matches[:limit]
    if not selected:
        return {
            "answer": "No encontré una política aprobada que responda esta consulta. El equipo de CUP&CAKE debe revisarla.",
            "claims": [],
            "citations": [],
            "evidence_status": "insufficient",
            "needs_human_review": True,
        }
    citations = []
    claims = []
    passages = []
    for index, item in enumerate(selected, start=1):
        citation_id = f"C{index}"
        citation = {"id": citation_id, **item["citation"]}
        citations.append(citation)
        claims.append({"text": item["content"], "citation_ids": [citation_id]})
        passages.append(f"{item['content']} [{citation_id}]")
    return {
        "answer": " ".join(passages),
        "claims": claims,
        "citations": citations,
        "evidence_status": "sufficient",
        "needs_human_review": False,
    }

