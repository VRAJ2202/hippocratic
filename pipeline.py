from categorizer import categorize
from storyteller import tell_story
from judge import judge_story, format_scores
from reviser import revise_story
from model import call_model

MAX_REVISIONS = 2

_FEEDBACK_SYSTEM = (
    "You are a responsive children's story editor. A child or parent has asked you to change a story. "
    "Honor their request fully — including changes to length, tone, and content. "
    "Two things must always be preserved: the five-beat arc structure "
    "(## Setup, ## Inciting Incident, ## Rising Action, ## Climax, ## Resolution) "
    "and age-appropriateness for readers aged 5–10."
)

_FEEDBACK_PROMPT = """The reader wants to change this story. Apply their request fully.

CURRENT STORY:
---
{story}
---

READER'S REQUEST: "{feedback}"

How to interpret common request types:
- Length change ("make it longer", "700 words", "shorter", "expand it"):
    Expand or compress proportionally across all five sections. "700 words" means target that word count total.
    "Longer" means add detail, dialogue, and sensory description to every section — do not pad with repetition.
    "Shorter" means trim every section to its essential beats.
- Tone change ("make it funnier", "more exciting", "calmer", "sillier"):
    Shift the language, pacing, and descriptions throughout — word choice, sentence rhythm, and dialogue should all reflect the new tone.
- Targeted change ("give the dragon a name", "add a sister", "change the ending"):
    Make only that specific change and leave everything else intact.
- Combined ("longer and funnier", "add a dog and make it calmer"):
    Apply all parts of the request together.

Keep all five section headers exactly as written:
## Setup, ## Inciting Incident, ## Rising Action, ## Climax, ## Resolution.
Output only the complete revised story — no commentary, no explanation."""


def _apply_user_feedback(story: str, feedback: str) -> str:
    prompt = _FEEDBACK_PROMPT.format(story=story, feedback=feedback)
    return call_model(prompt, max_tokens=1800, temperature=0.7, system=_FEEDBACK_SYSTEM)


def _print_divider(char="─", width=62):
    print(char * width)


def run_pipeline(request: str) -> str:
    # ── Step 1: Categorize ──────────────────────────────────────────
    print()
    _print_divider("─")
    print("[CATEGORIZER] Analyzing your request...")
    cat_result = categorize(request)
    category = cat_result["category"]
    print(f"[CATEGORIZER] Category : {category.upper()}")
    print(f"[CATEGORIZER] Reason   : {cat_result['reason']}")
    _print_divider("─")

    # ── Step 2: Generate story ──────────────────────────────────────
    print(f"\n[STORYTELLER] Writing a '{category}' story...")
    story = tell_story(request, category)
    print("[STORYTELLER] Story draft complete.")
    print(f"[STORYTELLER] Word count  : {len(story.split())} words")

    # ── Step 3: Judge → Revise loop ─────────────────────────────────
    revision_count = 0
    for iteration in range(MAX_REVISIONS + 1):
        label = "initial draft" if iteration == 0 else f"revision {iteration}"
        print(f"\n[JUDGE] Evaluating {label} (pass {iteration + 1} of {MAX_REVISIONS + 1})...")
        scores = judge_story(story, request)
        print(f"[JUDGE] Scores:\n{format_scores(scores)}")

        if scores["passes_threshold"]:
            print(f"\n[JUDGE] ✓ Story approved — overall {scores['overall']}/10 meets threshold.")
            break

        if iteration < MAX_REVISIONS:
            revision_count += 1
            fixes = ", ".join(scores["priority_fixes"]) or "general polish"
            print(f"\n[REVISER] Below threshold. Revision {revision_count}/{MAX_REVISIONS} targeting: {fixes}")
            story = revise_story(story, scores, request)
            print(f"[REVISER] Revision {revision_count} complete.")
        else:
            print(f"\n[REVISER] Max revisions ({MAX_REVISIONS}) reached — proceeding with best version.")

    print(f"\n[PIPELINE] Total revisions applied: {revision_count}")

    # ── Step 4: Present story ───────────────────────────────────────
    print()
    _print_divider("═")
    print("  YOUR STORY")
    _print_divider("═")
    print(story)
    _print_divider("═")

    # ── Step 5: User feedback loop ──────────────────────────────────
    print()
    while True:
        print("Would you like to change anything? (press Enter to finish)")
        user_feedback = input("  > ").strip()
        if not user_feedback:
            print("\nSweet dreams! Goodnight.")
            break
        print("\n[REVISER] Applying your changes...")
        story = _apply_user_feedback(story, user_feedback)
        print()
        _print_divider("═")
        print("  REVISED STORY")
        _print_divider("═")
        print(story)
        _print_divider("═")
        print()

    return story
