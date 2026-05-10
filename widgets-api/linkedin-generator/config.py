import os
from dataclasses import dataclass


DEFAULT_GATEWAY_URL = ""
DEFAULT_MODEL = "meta-llama/Llama-3.2-3B-Instruct"
DEFAULT_MAX_TOKENS = 512
DEFAULT_TEMPERATURE = 0.85
DEFAULT_TOP_P = 0.92


@dataclass(frozen=True)
class Settings:
    gateway_url: str
    model: str
    max_tokens: int
    temperature: float
    top_p: float


def _get_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    return int(value)


def _get_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None:
        return default
    return float(value)


def get_settings() -> Settings:
    return Settings(
        gateway_url=os.getenv("GATEWAY_URL", DEFAULT_GATEWAY_URL).strip(),
        model=os.getenv("MODEL", DEFAULT_MODEL),
        max_tokens=_get_int("MAX_TOKENS", DEFAULT_MAX_TOKENS),
        temperature=_get_float("TEMPERATURE", DEFAULT_TEMPERATURE),
        top_p=_get_float("TOP_P", DEFAULT_TOP_P),
    )
