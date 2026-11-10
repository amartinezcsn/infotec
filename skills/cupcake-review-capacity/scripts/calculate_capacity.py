#!/usr/bin/env python3
"""Calcula una señal de capacidad tentativa; nunca confirma disponibilidad."""

import argparse
import json
import sys


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--capacity-minutes", type=int, required=True)
    parser.add_argument("--reserved-minutes", type=int, required=True)
    parser.add_argument("--requested-minutes", type=int, required=True)
    parser.add_argument("--minimum-margin-percent", type=float, default=20.0)
    parser.add_argument("--blocked", action="store_true")
    args = parser.parse_args()

    if min(args.capacity_minutes, args.reserved_minutes, args.requested_minutes) < 0:
        print(json.dumps({"valid": False, "reason": "negative_minutes"}))
        return 2
    if args.reserved_minutes > args.capacity_minutes:
        print(json.dumps({"valid": False, "reason": "reserved_exceeds_capacity"}))
        return 2

    remaining_before = args.capacity_minutes - args.reserved_minutes
    remaining_after = remaining_before - args.requested_minutes
    required_margin = args.capacity_minutes * args.minimum_margin_percent / 100.0

    if args.blocked:
        status = "blocked"
        reasons = ["slot_blocked"]
    elif remaining_after < 0:
        status = "manual_review"
        reasons = ["estimated_effort_exceeds_remaining_capacity"]
    elif remaining_after < required_margin:
        status = "limited"
        reasons = ["capacity_margin_below_threshold"]
    else:
        status = "apparently_available"
        reasons = []

    print(json.dumps({
        "valid": True,
        "tentative_status": status,
        "remaining_before": remaining_before,
        "remaining_after": remaining_after,
        "reason_codes": reasons,
        "requires_human_review": True,
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
