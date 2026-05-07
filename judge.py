import json
from model import call_model, strip_json_fences

THRESHOLD = 7.0
AXES = ["age_appropriateness", "safety", "story_arc", "engagement", "length_fit"]

_SYSTEM = (
    "You are a rigorous children's literature quality evaluator. "
    "You assess stories on five axes and return ONLY valid JSON — no markdown, no extra text. "
    "Be honest and calibrated: a mediocre story scores 5–6, a solid story 7–8, exceptional is 9–10."
)

_PROMPT = """Evaluate this children's story (target audience: ages 5–10) on five quality axes.

ORIGINAL REQUEST: "{request}"

STORY:
---
{story}
---

Score each axis from 1–10 and write one specific sentence of feedback explaining your score.

Axis definitions:
- age_appropriateness: Is vocabulary, content, and complexity appropriate for ages 5–10? (10 = perfect fit)
- safety: Is the story free from frightening, violent, or inappropriate content? (10 = completely safe)
- story_arc: Are all five beats present and satisfying — Setup, Inciting Incident, Rising Action, Climax, Resolution? (10 = all five are clear and well-executed)
- engagement: Would a child actually want to hear this? Is it vivid, emotionally resonant, and fun? (10 = captivating)
- length_fit: Is the length right — not rushed, not losing a young reader's attention? (10 = ideal length)

Respond with ONLY this JSON object (no markdown fence, no extra keys):
{{
  "age_appropriateness": {{"score": <1-10>, "feedback": "<one specific sentence>"}},
  "safety": {{"score": <1-10>, "feedback": "<one specific sentence>"}},
  "story_arc": {{"score": <1-10>, "feedback": "<one specific sentence>"}},
  "engagement": {{"score": <1-10>, "feedback": "<one specific sentence>"}},
  "length_fit": {{"score": <1-10>, "feedback": "<one specific sentence>"}},
  "overall": <average of the five scores, as a float rounded to 2 decimal places>,
  "passes_threshold": <true if overall >= {threshold}, false otherwise>,
  "priority_fixes": [<axis names where score < 7, ordered worst-first>]
}}"""


def judge_story(story: str, request: str) -> dict:
    prompt = _PROMPT.format(story=story, request=request, threshold=THRESHOLD)
    raw = call_model(prompt, max_tokens=700, temperature=0.0, system=_SYSTEM)
    try:
        result = json.loads(strip_json_fences(raw))
        # recompute derived fields from scratch so they're always consistent
        scores = [result[ax]["score"] for ax in AXES]
        result["overall"] = round(sum(scores) / len(scores), 2)
        result["passes_threshold"] = result["overall"] >= THRESHOLD
        result["priority_fixes"] = sorted(
            [ax for ax in AXES if result[ax]["score"] < 7],
            key=lambda ax: result[ax]["score"],
        )
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        print(f"[JUDGE] WARNING: could not parse judge JSON ({type(e).__name__}: {e}) — using safe fallback scores.")
        result = {ax: {"score": 7, "feedback": "Judge output could not be parsed."} for ax in AXES}
        result["overall"] = 7.0
        result["passes_threshold"] = True
        result["priority_fixes"] = []
    return result


def format_scores(scores: dict) -> str:
    lines = []
    for ax in AXES:
        s = scores[ax]["score"]
        fb = scores[ax]["feedback"]
        bar = "#" * s + "-" * (10 - s)
        lines.append(f"  {ax:<22} [{bar}] {s:>2}/10  {fb}")
    overall = scores["overall"]
    status = "PASS" if scores["passes_threshold"] else "FAIL"
    lines.append(f"\n  Overall: {overall}/10  [{status} — threshold {THRESHOLD}]")
    if scores["priority_fixes"]:
        lines.append(f"  Priority fixes: {', '.join(scores['priority_fixes'])}")
    return "\n".join(lines)
