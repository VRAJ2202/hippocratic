"""
Before submitting the assignment, describe here in a few sentences what you would have built next if you spent 2 more hours on this project:

Three things. First, a character consistency tracker: a small dataclass built during the Outline step
that records each named character's physical description, personality, and any objects they carry.
The storyteller and reviser would receive this as a structured context block, preventing the common
GPT failure mode where a character's eye color or pet's fur changes mid-story. Second, streaming
output via stream=True so the story appears word-by-word in the terminal rather than all at once —
this dramatically improves the feeling of being read to and keeps a young listener engaged during
generation. Third, a minimal Streamlit front-end with a large-font, child-friendly layout, a
category picker with illustrated icons, and a "Read Aloud" button wired to the macOS `say` command
(or pyttsx3 cross-platform) — because a bedtime story tool that actually speaks the story aloud is
categorically more useful than one that prints to a terminal.
"""

example_requests = "A story about a girl named Alice and her best friend Bob, who happens to be a cat."


def main():
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║         Hippocratic AI Bedtime Story Generator               ║")
    print("║         For curious minds ages 5 to 10                      ║")
    print("╚══════════════════════════════════════════════════════════════╝")

    user_input = input("\nWhat kind of story do you want to hear?\n  > ").strip()
    if not user_input:
        user_input = example_requests
        print(f"  (No input — using example: {example_requests!r})")

    from pipeline import run_pipeline
    run_pipeline(user_input)


if __name__ == "__main__":
    main()
