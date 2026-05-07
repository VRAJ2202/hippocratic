import json
from model import call_model, strip_json_fences

CATEGORIES = ["adventure", "friendship", "silly/funny", "calming-bedtime", "educational"]

_SYSTEM = """You are a children's story classifier. You respond with ONLY valid JSON — no markdown, no explanation, no extra text."""

_PROMPT = """Classify this story request into exactly one of these five categories:
- adventure: journeys, exploration, quests, heroes, action, danger
- friendship: bonds, kindness, teamwork, making or keeping friends
- silly/funny: humor, absurdity, jokes, slapstick, funny animals
- calming-bedtime: peaceful, gentle, soothing, stars, cozy, sleep
- educational: learning a fact, science, nature, history, how things work

Story request: "{request}"

Respond with ONLY this JSON (no markdown fence, no extra keys):
{{"category": "<one of the five categories>", "reason": "<one sentence why>"}}"""


def categorize(request: str) -> dict:
    raw = call_model(
        _PROMPT.format(request=request),
        max_tokens=150,
        temperature=0.0,
        system=_SYSTEM,
    )
    try:
        result = json.loads(strip_json_fences(raw))
        if result.get("category") not in CATEGORIES:
            result["category"] = "adventure"
            result["reason"] = "Category not recognized — defaulted to adventure."
    except (json.JSONDecodeError, KeyError):
        result = {"category": "adventure", "reason": "Parse error — defaulted to adventure."}
    return result
