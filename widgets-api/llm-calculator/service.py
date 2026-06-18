from gateway_wrapper import generate_text

SYSTEM_PROMPT = """You are a calculator, which generates correct answers to arithmetic questions posed by the user. Answer with ONLY the numerical output of the answer - no text. Answer as accurately as possible, to as many decimal places as required. Here are some examples of questions and answers you may see:
    
USER: 4+8
CHATBOT: 12

---

USER: 182*526
CHATBOT: 95732

---

USER: 97.35/15.02
CHATBOT: 6.48135818908

"""


def llm_calculate(left_num: float, operation: str, right_num: float) -> str:
    """Ask the model gateway to calculate an arithmetic expression."""
    input_text = f"{left_num} {operation} {right_num}"
    response = generate_text(input_text=input_text, system_prompt=SYSTEM_PROMPT)
    return str(response["content"]).strip()
