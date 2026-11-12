from app.services.state_machine import validate_transition


def test_agent_cannot_approve_availability():
    valid, reason = validate_transition("pending_availability_review", "availability_approved", "agent")
    assert valid is False
    assert reason == "human_approval_required"


def test_human_can_approve_availability():
    valid, reason = validate_transition("pending_availability_review", "availability_approved", "human_staff")
    assert valid is True
    assert reason == "allowed"

