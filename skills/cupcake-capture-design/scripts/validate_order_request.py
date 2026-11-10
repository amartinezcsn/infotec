#!/usr/bin/env python3
"""Valida la estructura mínima de una solicitud personalizada desde JSON."""

import argparse
import json
import sys
from datetime import datetime


ALLOWED_CATEGORIES = {"pasteles-personalizados", "cupcakes", "galletas-decoradas"}
ALLOWED_MODES = {"delivery", "pickup"}


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("json_file")
    args = parser.parse_args()

    with open(args.json_file, "r", encoding="utf-8") as handle:
        data = json.load(handle)

    missing = []
    product = data.get("product") or {}
    if product.get("category") not in ALLOWED_CATEGORIES:
        missing.append("product.category")
    for field in ("product_id", "name", "kyte_url", "last_synced_at"):
        if not nonempty(product.get(field)):
            missing.append(f"product.{field}")
    for field in ("quantity_or_portions", "flavor", "theme"):
        if not nonempty(data.get(field)):
            missing.append(field)
    if data.get("fulfillment_mode") not in ALLOWED_MODES:
        missing.append("fulfillment_mode")
    try:
        datetime.fromisoformat(str(data.get("requested_at", "")).replace("Z", "+00:00"))
    except ValueError:
        missing.append("requested_at")
    if data.get("customer_confirmed_summary") is not True:
        missing.append("customer_confirmed_summary")

    result = {"valid": not missing, "missing_or_invalid": sorted(set(missing))}
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["valid"] else 2


if __name__ == "__main__":
    sys.exit(main())
