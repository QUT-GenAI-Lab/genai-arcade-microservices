from typing import Any

from models import get_available_models, Model


def generate(
    messages: list[dict[str, str]],
    model: str,
    max_tokens: int = 512,
    temperature: float = 0.7,
    top_p: float = 0.9,
    stop: list[str] | None = None,
) -> dict[str, Any]:
    if model == Model.LLAMA_3_2_3B_INSTRUCT.model_id:
        from models import llama

        return llama.generate(
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            stop=stop,
        )
    if model == Model.GEMMA_4_E2B.model_id:
        from models import gemma4_e2b

        return gemma4_e2b.generate(
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
