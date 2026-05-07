import os
import re
import openai
from dotenv import load_dotenv

load_dotenv()


def call_model(prompt: str, max_tokens=3000, temperature=0.1, system=None) -> str:
    openai.api_key = os.getenv("OPENAI_API_KEY")
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    resp = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        stream=False,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return resp.choices[0].message["content"]  # type: ignore


def strip_json_fences(text: str) -> str:
    """Remove markdown code fences that GPT sometimes wraps JSON in."""
    text = text.strip()
    match = re.match(r"^```(?:json)?\s*(.*?)\s*```$", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text
