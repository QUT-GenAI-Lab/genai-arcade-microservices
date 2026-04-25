import gradio
from service import llama_calculator

app = gradio.Server()


@app.api_route("/calculate", response_model=str)
def calculate(left_num: float, operation: str, right_num: float) -> str:
    return llama_calculator(left_num, operation, right_num)
