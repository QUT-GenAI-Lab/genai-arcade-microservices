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
    # Ensure model exists
    if model not in [m["id"] for m in get_available_models()]:
        msg = f"Model '{model}' is not available. Supported models: {[m['id'] for m in get_available_models()]}"
        raise ValueError(msg)
    if model == Model.LLAMA_3_2_3B_INSTRUCT.model_id:
        from models.llama3_2_3b_instruct import generate
    if model == Model.GEMMA_4_E2B.model_id:
        from models.gemma4_e2b import generate
    return generate(  # type: ignore
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
        stop=stop,
    )


def list_models() -> dict[str, list[dict[str, Any]]]:
    return {"models": get_available_models()}
