# Hippocratic AI Coding Assignment
Welcome to the [Hippocratic AI](https://www.hippocraticai.com) coding assignment

## Instructions
The attached code is a simple python script skeleton. Your goal is to take any simple bedtime story request and use prompting to tell a story appropriate for ages 5 to 10.
- Incorporate a LLM judge to improve the quality of the story
- Provide a block diagram of the system you create that illustrates the flow of the prompts and the interaction between judge, storyteller, user, and any other components you add
- Do not change the openAI model that is being used. 
- Please use your own openAI key, but do not include it in your final submission.
- Otherwise, you may change any code you like or add any files

---

## Rules
- This assignment is open-ended
- You may use any resources you like with the following restrictions
   - They must be resources that would be available to you if you worked here (so no other humans, no closed AIs, no unlicensed code, etc.)
   - Allowed resources include but not limited to Stack overflow, random blogs, chatGPT et al
   - You have to be able to explain how the code works, even if chatGPT wrote it
- DO NOT PUSH THE API KEY TO GITHUB. OpenAI will automatically delete it

---

## What does "tell a story" mean?
It should be appropriate for ages 5-10. Other than that it's up to you. Here are some ideas to help get the brain-juices flowing!
- Use story arcs to tell better stories
- Allow the user to provide feedback or request changes
- Categorize the request and use a tailored generation strategy for each category

---

## How will I be evaluated
Good question. We want to know the following:
- The efficacy of the system you design to create a good story
- Are you comfortable using and writing a python script
- What kinds of prompting strategies and agent design strategies do you use
- Are the stories your tool creates good?
- Can you understand and deconstruct a problem
- Can you operate in an open-ended environment
- Can you surprise us

---

## Other FAQs
- How long should I spend on this? 
No more than 2-3 hours
- Can I change what the input is? 
Sure
- How long should the story be?
You decide

---

# My Implementation

## Setup

**Requirements:** Python 3.8+, an OpenAI API key.

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set your API key
cp .env.example .env
# then open .env and replace the placeholder with your key
```

## How to Run

```bash
python main.py
```

You'll be prompted to describe the story you want. The pipeline prints each stage as it runs so you can follow along.

```
What kind of story do you want to hear?
  > A silly story about a penguin who desperately wants to fly
```

---

## Architecture

The system is a five-stage sequential pipeline. Each stage is its own module with a single responsibility.

```
User Input
    │
    ▼
[categorizer.py]   → classifies genre (adventure / friendship / silly/funny /
    │                 calming-bedtime / educational), outputs JSON
    ▼
[storyteller.py]   → generates 5-beat story draft using a category-specific
    │                 system prompt and an arc-enforcing user prompt
    ▼
[judge.py]         → scores 5 axes (age-appropriateness, safety, story arc,
    │                 engagement, length-fit), returns structured JSON
    │
    ├─ overall ≥ 7.0 ──────────────────────────────┐
    │                                               │
    └─ below threshold (max 2 passes) ──►  [reviser.py]  ──► judge again
                                                    │
                                                    ▼
                                           Present story to user
                                                    │
                                           User feedback loop
                                           (free-text → reviser → repeat)
```

See `DIAGRAM.md` for a full Mermaid flowchart with color-coded components.

### Module breakdown

| File | Role |
|---|---|
| `model.py` | Shared `call_model` wrapper; all LLM calls go through here |
| `categorizer.py` | Zero-shot genre classifier |
| `storyteller.py` | Category-specific story generator with enforced arc structure |
| `judge.py` | Rubric-based evaluator; outputs structured JSON scores |
| `reviser.py` | Surgical rewriter that targets only failing axes |
| `pipeline.py` | Orchestrates the full flow; handles the judge–revise loop and user feedback |
| `main.py` | Entry point; preserves original `call_model` signature |

---

## Prompting Strategies

**Categorizer — zero-shot classification at temperature 0.0**
Strict JSON output (`{category, reason}`) with definitions for each genre listed in the prompt. Temperature 0 for determinism. A code-level fallback handles any parse failure.

**Storyteller — persona + arc enforcement**
Two-part prompt: a category-specific system prompt sets a named persona and tone rules (e.g. for `calming-bedtime`: *"longer, lilting sentences; soft imagery; no loud moments"*), and the user prompt demands the story be written under five explicit labeled headers (`## Setup`, `## Inciting Incident`, `## Rising Action`, `## Climax`, `## Resolution`). Naming the sections as headers forces structure rather than hoping the model produces it. Temperature 0.75 for creative range within those constraints.

**Judge — rubric scoring at temperature 0.0**
Each of the five axes has a written definition in the prompt. The system prompt calibrates the scale ("mediocre = 5–6, solid = 7–8, exceptional = 9–10") to prevent grade inflation. Derived fields (`overall`, `passes_threshold`, `priority_fixes`) are recomputed in Python from the raw scores — the model only needs to produce per-axis numbers, which reduces hallucination surface area.

**Auto-Reviser — dynamic, surgical prompt**
The revision prompt is built at runtime: only the axes that scored below 7 are included in the `JUDGE FEEDBACK TO ADDRESS` block, and the model is explicitly told to leave sections that scored 8+ unchanged. This prevents the model from "fixing" things that weren't broken. Temperature 0.6 — focused but not rigid.

**User-Feedback Reviser — open-ended at temperature 0.7**
Free-text feedback from the user is passed directly into a short prompt that applies only the requested change while preserving the arc structure. Higher temperature allows the model to interpret vague requests like *"make it funnier"* or *"give the dragon a name"* creatively.

---

## Example Runs

**Input:** `A silly story about a penguin who desperately wants to fly`

```
[CATEGORIZER] Category : SILLY/FUNNY
[CATEGORIZER] Reason   : The premise of a penguin attempting flight is inherently absurd and comedic.

[STORYTELLER] Writing a 'silly/funny' story...
[STORYTELLER] Story draft complete.

[JUDGE] Evaluating initial draft (pass 1 of 3)...
[JUDGE] Scores:
  age_appropriateness    [########--]  8/10  Vocabulary is simple and accessible for ages 5–10.
  safety                 [##########] 10/10  Completely safe and cheerful throughout.
  story_arc              [######----]  6/10  The climax arrives abruptly with little rising tension.
  engagement             [########--]  8/10  The fish-catapult scene will genuinely make kids laugh.
  length_fit             [#######---]  7/10  Slightly short — the rising action could breathe more.

  Overall: 7.8/10  [PASS — threshold 7.0]

[JUDGE] ✓ Story approved — overall 7.8/10 meets threshold.
[PIPELINE] Total revisions applied: 0
```

---

**Input:** `A bedtime story about a little bear who can't fall asleep`

```
[CATEGORIZER] Category : CALMING-BEDTIME
[CATEGORIZER] Reason   : A bear struggling to sleep is a classic, soothing bedtime premise.

[STORYTELLER] Writing a 'calming-bedtime' story...

[JUDGE] Evaluating initial draft (pass 1 of 3)...
[JUDGE] Scores:
  age_appropriateness    [########--]  8/10  Gentle language well-suited for young readers.
  safety                 [##########] 10/10  Entirely peaceful with no frightening elements.
  story_arc              [#####-----]  5/10  Resolution is present but the inciting incident is vague.
  engagement             [######----]  6/10  Imagery is soft but the middle section loses momentum.
  length_fit             [########--]  8/10  Appropriate length for a bedtime read-aloud.

  Overall: 7.4/10  [FAIL — threshold 7.0]
  Priority fixes: story_arc, engagement

[REVISER] Below threshold. Revision 1/2 targeting: story_arc, engagement
[REVISER] Revision 1 complete.

[JUDGE] Evaluating revision 1 (pass 2 of 3)...
[JUDGE] Scores:
  ...
  Overall: 8.1/10  [PASS — threshold 7.0]

[JUDGE] ✓ Story approved — overall 8.1/10 meets threshold.
[PIPELINE] Total revisions applied: 1
```

---

## Design Decisions

**Why split into separate modules?**
Each stage has a different job, a different temperature, and a different failure mode. Keeping them separate means you can tune, test, or replace any one component without touching the others. The judge in particular needs to be isolated — if it lived inside the storyteller it couldn't give honest feedback on its own output.

**Why enforce the arc in the prompt rather than in post-processing?**
Asking the model to label sections with explicit headers (`## Climax`) is cheaper and more reliable than parsing free-form prose to detect story beats after the fact. It also makes the judge's `story_arc` scoring simpler — the judge can see at a glance whether all five sections exist.

**Why does the reviser only target failing axes?**
A full rewrite risks degrading sections that were already good. By building the revision prompt from only the low-scoring axes, the reviser acts like a copy editor rather than a ghostwriter — it patches, not replaces.

**Why temperature 0.0 for the categorizer and judge?**
Classification and evaluation should be deterministic and reproducible. Creativity is useful in the storyteller and reviser, not in components whose job is to make consistent decisions.

**What I'd build with 2 more hours:**
1. **Character consistency tracker** — a small dataclass built at the outline stage that records each character's name, description, and carried objects. Passed to the storyteller and reviser as a structured context block, preventing continuity errors mid-story (e.g. a cat described as orange turning grey in the climax).
2. **Streaming output** — `stream=True` so the story appears word-by-word rather than all at once. This transforms the feel from "waiting for a print statement" to "being read to."
3. **Read-aloud front-end** — a minimal Streamlit UI with large fonts, a category picker with icons, and a "Read Aloud" button wired to `say` (macOS) or `pyttsx3` cross-platform. A bedtime story tool that speaks the story aloud is categorically more useful than one that prints to a terminal.