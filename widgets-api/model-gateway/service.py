from typing import Any

from models import get_available_models
from models.llama import LlamaModel


def generate(
    messages: list[dict[str, str]],
    model: str = LlamaModel.MODEL_ID,
    max_tokens: int = 512,
    temperature: float = 0.7,
    top_p: float = 0.9,
    stop: list[str] | None = None,
) -> dict[str, Any]:
    if model == LlamaModel.MODEL_ID:
        return LlamaModel.generate(
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            stop=stop,
        )
    msg = f"Unsupported model: {model}"
    raise ValueError(msg)


def list_models() -> dict[str, list[dict[str, Any]]]:
    return {"models": get_available_models()}
