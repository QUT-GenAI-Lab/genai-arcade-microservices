from typing import Any
from enum import Enum


class Model(Enum):
    LLAMA_3_2_3B_INSTRUCT = (
        "meta-llama/Llama-3.2-3B-Instruct",
        "text-generation",
        "local",
        4096,
    )
    GEMMA_4_E2B = ("google/gemma-4-E2B-it", "text-generation", "local", 4096)

    def __init__(
        self,
        model_id: str,
        model_type: str,
        backend: str,
        max_tokens: int,
    ):
        self.model_id = model_id
        self.model_type = model_type
        self.backend = backend
        self.max_tokens = max_tokens

    def __str__(self):
        return self.model_id

    def __repr__(self):
        return f"Model(id={self.model_id}, type={self.model_type}, backend={self.backend}, max_tokens={self.max_tokens})"

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.model_id,
            "type": self.model_type,
            "backend": self.backend,
            "max_tokens": self.max_tokens,
        }


AVAILABLE_MODELS = [model.to_dict() for model in Model]


def get_available_models() -> list[dict[str, Any]]:
    return AVAILABLE_MODELS
