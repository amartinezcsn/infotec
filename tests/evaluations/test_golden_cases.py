import json
from pathlib import Path

from app.services.agent import respond


def test_golden_intent_routing(client):
    cases = json.loads((Path(__file__).with_name("golden_cases.json")).read_text(encoding="utf-8"))
    for case in cases:
        result = respond(case["input"])
        assert result["intent"] == case["expected_intent"]
        assert result["requires_human_review"] is case["must_require_human_review"]
