from __future__ import annotations

from datetime import datetime

from ..db import fetch_one


def check_tentative_capacity(requested_at: datetime, requested_minutes: int, margin_percent: float = 20.0) -> dict:
    slot_date = requested_at.date().isoformat()
    slot = fetch_one("SELECT * FROM capacity_slots WHERE slot_date = ?", (slot_date,))
    capacity = int(slot["capacity_minutes"]) if slot else 480
    reserved = int(slot["reserved_minutes"]) if slot else 0
    blocked = bool(slot["blocked"]) if slot else False
    before = capacity - reserved
    after = before - requested_minutes
    required_margin = capacity * margin_percent / 100
    if blocked:
        status, reasons = "blocked", ["slot_blocked"]
    elif after < 0:
        status, reasons = "manual_review", ["estimated_effort_exceeds_remaining_capacity"]
    elif after < required_margin:
        status, reasons = "limited", ["capacity_margin_below_threshold"]
    else:
        status, reasons = "apparently_available", []
    return {
        "requested_at": requested_at.isoformat(),
        "tentative_status": status,
        "capacity_basis": {"capacity_minutes": capacity, "reserved_minutes": reserved, "requested_minutes": requested_minutes},
        "remaining_after": after,
        "reason_codes": reasons,
        "alternative_dates": [],
        "requires_human_review": True,
    }

