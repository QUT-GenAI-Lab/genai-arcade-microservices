from typing import Any

import spaces
from models.llama import LlamaModel
import gradio

from service import generate, list_models

app = gradio.Server()


@app.api(name="generate", description="Text generation using a chat template.")
@spaces.GPU(duration=10)
def generate_endpoint(
    messages: list[dict[str, str]],
    model: str = LlamaModel.MODEL_ID,
    max_tokens: int = 512,
    temperature: float = 0.7,
    top_p: float = 0.9,
    stop: list[str] | None = None,
) -> dict[str, Any]:
    return generate(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
        stop=stop,
    )


@app.api(name="models", description="List available models and their capabilities.")
def models_endpoint() -> dict[str, list[dict[str, Any]]]:
    return list_models()


app.launch()
