from typing import Any

import gradio

from gateway_wrapper import check_gateway_health
from service import llm_calculate

app = gradio.Server()


@app.api(
    name="health",
    description="Check whether the model gateway is configured and ready.",
)
def health() -> dict[str, Any]:
    return check_gateway_health()


@app.api(
    name="calculate",
    description="Calculate the result of an arithmetic operation between two numbers.",
)
def calculate(left_num: float, operation: str, right_num: float) -> str:
    return llm_calculate(left_num, operation, right_num)


app.launch()
