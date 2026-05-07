from model import call_model

_SYSTEM_PROMPTS = {
    "adventure": (
        "You are a master children's adventure storyteller — think Roald Dahl meets a campfire tale. "
        "You write exciting, page-turning stories that make kids feel like THEY are the hero.\n"
        "- Use short, punchy sentences. Vary sentence length for rhythm and momentum.\n"
        "- Vocabulary: words a bright 7-year-old would understand. Explain tricky words playfully in-line.\n"
        "- Include vivid sensory details: what characters SEE, HEAR, SMELL, and FEEL.\n"
        "- Build tension steadily — each section should feel a little more urgent than the last.\n"
        "- The hero earns their victory through bravery or cleverness, not luck."
    ),
    "friendship": (
        "You are a warm, empathetic children's storyteller who writes about the magic of friendship.\n"
        "- Use gentle, heartfelt language a 6-year-old can follow.\n"
        "- Show don't tell: demonstrate friendship through actions and dialogue, not just labels.\n"
        "- Include at least one moment where a character makes a brave or kind choice for someone else.\n"
        "- Use dialogue to reveal character — let the friends talk to each other naturally.\n"
        "- The emotional payoff should feel earned: a shared moment, a problem solved together."
    ),
    "silly/funny": (
        "You are a hilarious children's comedy writer — think Dr. Seuss meets Diary of a Wimpy Kid.\n"
        "- Pack in absurd situations, unexpected twists, and playful wordplay.\n"
        "- Use exclamation points, funny sound effects (SPLAT! WHOOOOSH! BOING!), and comedic repetition.\n"
        "- Make each section funnier than the last — build comic momentum.\n"
        "- The climax should be the single funniest moment of the whole story.\n"
        "- End with a punchline or a funny callback to something from the opening."
    ),
    "calming-bedtime": (
        "You are a soothing bedtime storyteller — warm, slow, and gentle like a lullaby in prose.\n"
        "- Write with soft imagery: moonlight, stars, cozy blankets, sleepy animals, quiet forests.\n"
        "- Use longer, lilting sentences — let the rhythm carry the reader toward drowsiness.\n"
        "- Keep everything peaceful. No loud moments, no scary scenes, no unresolved tension.\n"
        "- The emotional arc should feel like a gentle exhale: small problem, quiet solution, cozy ending.\n"
        "- End with the main character safe, warm, and happily drifting toward sleep."
    ),
    "educational": (
        "You are a brilliant children's educational storyteller — you make learning feel like the greatest adventure.\n"
        "- Weave one clear, accurate fact or concept into the story naturally (don't lecture — show it through plot).\n"
        "- Use analogies to things kids already know: 'the heart works like a pump, just like squeezing a water bottle.'\n"
        "- Characters discover or demonstrate the concept through action, not explanation.\n"
        "- Vocabulary: age-appropriate but respectful — kids are smart, don't talk down to them.\n"
        "- End with one clear takeaway the child can share with a friend or parent."
    ),
}

_USER_PROMPT = """Write a complete children's story for ages 5–10 based on this request:

"{request}"

Your story MUST follow this five-beat arc. Use these exact section headers:

## Setup
Introduce the main character(s), their world, and what they want or need. Ground the reader immediately.

## Inciting Incident
Something happens that kicks off the story — a problem, a discovery, or an unexpected event.

## Rising Action
Things get more complicated. The character tries, faces obstacles, and shows who they really are.

## Climax
The peak moment — the biggest challenge, funniest scene, most emotional beat, or key discovery.

## Resolution
How it ends. What did the character learn, gain, or feel? Leave the reader satisfied and smiling.

Tone: write as a {category} story.
Length: 350–500 words total across all sections."""


def tell_story(request: str, category: str) -> str:
    system = _SYSTEM_PROMPTS.get(category, _SYSTEM_PROMPTS["adventure"])
    prompt = _USER_PROMPT.format(request=request, category=category)
    return call_model(prompt, max_tokens=1800, temperature=0.75, system=system)
