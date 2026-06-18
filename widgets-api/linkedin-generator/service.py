from gateway_wrapper import generate_text
from typing import Any

SYSTEM_PROMPT = """You are now a LinkedIn post generator. I will just give you a fraction of an idea and you will convert it into a buzzing LinkedIn post full of emojis and excitement, just like every other LinkedIn post. Give me one post without any explanation."""


def generate_linkedin_post(input_text: str) -> dict[str, Any]:
    return generate_text(input_text=input_text, system_prompt=SYSTEM_PROMPT)
