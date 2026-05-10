from typing import Any

from gateway import generate as generate_text

SYSTEM_PROMPT = """You are now a LinkedIn post generator. I will just give you a fraction of an idea and you will convert it into a buzzing LinkedIn post full of emojis and excitement, just like every other LinkedIn post. Give me one post without any explanation."""


def generate_linkedin_post(input_text: str) -> dict[str, Any]:
    prompt = input_text.strip()
    if not prompt:
        raise ValueError("input_text must not be empty.")

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]

    generation = generate_text(messages=messages)

    return {
        "content": generation["content"],
        "model": generation["model"],
        "usage": generation["usage"],
        "source_text": prompt,
    }
