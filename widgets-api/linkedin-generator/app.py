from typing import Any

import gradio

from gateway import check_gateway_health
from service import generate_linkedin_post

app = gradio.Server()


@app.api(
    name="health",
    description="Check whether the model gateway is configured and ready.",
)
def health() -> dict[str, Any]:
    return check_gateway_health()


@app.api(
    name="generate",
    description="Convert plain text into a LinkedIn-style post through the model gateway.",
)
def generate(input_text: str) -> dict[str, Any]:
    return generate_linkedin_post(input_text)


app.launch()
