#!/usr/bin/env python3
"""Comprueba que una respuesta RAG tenga citas aprobadas por afirmación."""

import argparse
import json
import sys


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("json_file")
    args = parser.parse_args()

    with open(args.json_file, "r", encoding="utf-8") as handle:
        data = json.load(handle)

    errors = []
    citations = data.get("citations") or []
    citation_map = {item.get("id"): item for item in citations if item.get("id")}
    for citation in citations:
        if citation.get("status") != "approved":
            errors.append(f"citation_not_approved:{citation.get('id')}")
        for field in ("document_id", "title", "section", "version"):
            if not citation.get(field):
                errors.append(f"citation_missing_{field}:{citation.get('id')}")

    for index, claim in enumerate(data.get("claims") or []):
        ids = claim.get("citation_ids") or []
        if not ids:
            errors.append(f"claim_without_citation:{index}")
        for citation_id in ids:
            if citation_id not in citation_map:
                errors.append(f"unknown_citation:{citation_id}")

    status = data.get("evidence_status")
    if status not in {"sufficient", "insufficient", "conflicting"}:
        errors.append("invalid_evidence_status")
    if status != "sufficient" and data.get("needs_human_review") is not True:
        errors.append("human_review_required")

    result = {"valid": not errors, "errors": errors}
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["valid"] else 2


if __name__ == "__main__":
    sys.exit(main())
