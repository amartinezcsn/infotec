#!/usr/bin/env python3
"""Valida un análisis OCR y deriva su estado preliminar no vinculante."""

import argparse
import json
import sys
from decimal import Decimal, InvalidOperation


CRITICAL = ("transaction_date", "amount", "currency")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("json_file")
    parser.add_argument("--confidence-threshold", type=float, default=0.75)
    args = parser.parse_args()

    with open(args.json_file, "r", encoding="utf-8") as handle:
        data = json.load(handle)

    errors = []
    fields = data.get("extracted_fields") or {}
    confidence = data.get("confidence") or {}
    if not data.get("document_id"):
        errors.append("missing_document_id")
    if not data.get("file_hash"):
        errors.append("missing_file_hash")

    missing = [field for field in CRITICAL if fields.get(field) in (None, "")]
    if not fields.get("reference") and not fields.get("tracking_key"):
        missing.append("reference_or_tracking_key")

    low = [field for field in CRITICAL if float(confidence.get(field, 0)) < args.confidence_threshold]
    duplicate = bool((data.get("duplicate_signals") or {}).get("hash_match"))

    mismatch = False
    try:
        extracted = Decimal(str(fields.get("amount")))
        expected = Decimal(str((data.get("expected_deposit") or {}).get("amount")))
        extracted_currency = fields.get("currency")
        expected_currency = (data.get("expected_deposit") or {}).get("currency")
        mismatch = extracted != expected or extracted_currency != expected_currency
    except (InvalidOperation, TypeError):
        missing.append("comparable_amount")

    if errors:
        status = "invalid_analysis"
    elif missing:
        status = "unreadable"
    elif duplicate:
        status = "duplicate_suspected"
    elif mismatch:
        status = "amount_mismatch"
    elif low:
        status = "low_confidence"
    else:
        status = "ready_for_human_review"

    result = {
        "valid": not errors,
        "errors": errors,
        "missing_fields": sorted(set(missing)),
        "low_confidence_fields": sorted(set(low)),
        "preliminary_status": status,
        "requires_human_review": True,
    }
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["valid"] else 2


if __name__ == "__main__":
    sys.exit(main())
