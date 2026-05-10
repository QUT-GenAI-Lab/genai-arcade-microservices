from dataclasses import dataclass
from typing import Any
from enum import Enum


@dataclass
class ModelUsage:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


@dataclass
class TextGenerationResult:
    content: str
    model: str
    usage: ModelUsage


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
        id: str,
        model_type: str,
        backend: str,
        max_tokens: int,
    ):
        self.id = id
        self.model_type = model_type
        self.backend = backend
        self.max_tokens = max_tokens

    def __str__(self):
        return self.id

    def __repr__(self):
        return f"Model(id={self.id}, type={self.model_type}, backend={self.backend}, max_tokens={self.max_tokens})"

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": self.model_type,
            "backend": self.backend,
            "max_tokens": self.max_tokens,
        }


AVAILABLE_MODELS = [model for model in Model]


def get_available_models():
    return AVAILABLE_MODELS
