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


def validate_transition(current: str, target: str, actor_type: str) -> tuple[bool, str]:
    if target not in ALLOWED.get(current, set()):
        return False, "transition_not_allowed"
    if (current, target) in HUMAN_ONLY and actor_type != "human_staff":
        return False, "human_approval_required"
    return True, "allowed"

