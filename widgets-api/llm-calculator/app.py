import gradio
from service import llama_calculator

app = gradio.Server()


@app.api(
    name="calculate",
    description="Calculate the result of an arithmetic operation between two numbers.",
)
def calculate(left_num: float, operation: str, right_num: float) -> str:
    return llama_calculator(left_num, operation, right_num)


app.launch()
