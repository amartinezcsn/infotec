#!/usr/bin/env python3
"""Valida transiciones de pedido y puertas de aprobación humana."""

import argparse
import json
import sys


ALLOWED = {
    "draft": {"requirements_incomplete", "pending_availability_review", "cancelled"},
    "requirements_incomplete": {"pending_availability_review", "cancelled"},
    "pending_availability_review": {"availability_approved", "alternative_proposed", "availability_rejected", "cancelled"},
    "alternative_proposed": {"pending_availability_review", "availability_rejected", "cancelled"},
    "availability_approved": {"quote_pending", "cancelled"},
    "quote_pending": {"quote_sent", "cancelled"},
    "quote_sent": {"awaiting_deposit", "cancelled"},
    "awaiting_deposit": {"payment_proof_under_review", "cancelled"},
    "payment_proof_under_review": {"confirmed", "awaiting_deposit", "cancelled"},
    "confirmed": {"in_design", "cancelled"},
    "in_design": {"in_production", "cancelled"},
    "in_production": {"ready_for_delivery", "cancelled"},
    "ready_for_delivery": {"completed", "cancelled"},
}

HUMAN_ONLY = {
    ("pending_availability_review", "availability_approved"),
    ("pending_availability_review", "alternative_proposed"),
    ("pending_availability_review", "availability_rejected"),
    ("quote_pending", "quote_sent"),
    ("payment_proof_under_review", "confirmed"),
    ("payment_proof_under_review", "awaiting_deposit"),
    ("confirmed", "in_design"),
    ("in_design", "in_production"),
    ("in_production", "ready_for_delivery"),
    ("ready_for_delivery", "completed"),
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("current")
    parser.add_argument("next")
    parser.add_argument("--actor-type", choices=["customer", "agent", "human_staff", "system"], required=True)
    args = parser.parse_args()

    pair = (args.current, args.next)
    valid = args.next in ALLOWED.get(args.current, set())
    reason = "allowed" if valid else "transition_not_allowed"
    if valid and pair in HUMAN_ONLY and args.actor_type != "human_staff":
        valid = False
        reason = "human_approval_required"

    print(json.dumps({"valid": valid, "reason": reason}, ensure_ascii=False))
    return 0 if valid else 2


if __name__ == "__main__":
    sys.exit(main())
