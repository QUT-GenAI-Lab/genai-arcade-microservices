from typing import Any


AVAILABLE_MODELS: list[dict[str, Any]] = [
    {
        "id": "meta-llama/Llama-3.2-3B-Instruct",
        "type": "text-generation",
        "backend": "local",
        "max_tokens": 4096,
    },
]


def get_available_models() -> list[dict[str, Any]]:
    return AVAILABLE_MODELS
