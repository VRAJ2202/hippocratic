from model import call_model

_SYSTEM = (
    "You are a surgical children's story editor. You make targeted improvements based on specific feedback. "
    "You do NOT rewrite the whole story — you keep what works and fix only what needs fixing. "
    "Always preserve the five-beat arc structure and the same characters, setting, and tone."
)

_PROMPT = """You are revising a children's story (ages 5–10). Apply the specific judge feedback below — and only that feedback.

ORIGINAL REQUEST: "{request}"

ORIGINAL STORY:
---
{story}
---

JUDGE FEEDBACK TO ADDRESS:
{feedback_block}

REVISION RULES:
- Fix ONLY the issues listed above. Do not change sections that scored 8 or higher.
- Keep the exact same characters, setting, and story category tone.
- Maintain all five section headers: ## Setup, ## Inciting Incident, ## Rising Action, ## Climax, ## Resolution.
- Output the complete revised story — all five sections — even the ones you didn't change.
- Do not add commentary or explain your changes. Just output the story."""


def _build_feedback_block(scores: dict, priority_fixes: list) -> str:
    if not priority_fixes:
        return "No major issues — do a light pass for flow, word choice, and rhythm."
    lines = []
    for ax in priority_fixes:
        s = scores[ax]["score"]
        fb = scores[ax]["feedback"]
        lines.append(f"- {ax} (score {s}/10): {fb}")
    return "\n".join(lines)


def revise_story(story: str, scores: dict, request: str) -> str:
    priority_fixes = scores.get("priority_fixes", [])
    feedback_block = _build_feedback_block(scores, priority_fixes)
    prompt = _PROMPT.format(request=request, story=story, feedback_block=feedback_block)
    return call_model(prompt, max_tokens=1800, temperature=0.6, system=_SYSTEM)
