from datetime import datetime

from app.services.capacity import check_tentative_capacity


def test_capacity_is_always_tentative(client):
    result = check_tentative_capacity(datetime(2027, 1, 10, 12, 0), 120)
    assert result["tentative_status"] == "apparently_available"
    assert result["requires_human_review"] is True

