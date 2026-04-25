import spaces
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from transformers import pipeline


# Llama 3.2 1b setup
# quantization_config = BitsAndBytesConfig(load_in_4bit=True)
torch_device = (
    "cuda"
    if torch.cuda.is_available()
    else ("mps" if torch.backends.mps.is_available() else "cpu")
)

torch_dtype = torch.bfloat16 if torch_device in ["cuda", "mps"] else torch.float32

llama_model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.2-3B-Instruct",
    #  quantization_config=quantization_config,
    torch_dtype=torch_dtype,
    device_map=torch_device,
    # load_in_4bit=True #for puny devices like mine.
)

llama_tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.2-3B-Instruct")


model_id = "meta-llama/Llama-3.2-3B-Instruct"
pipe = pipeline(
    "text-generation",
    model=llama_model,
    tokenizer=llama_tokenizer,
    torch_dtype=torch.bfloat16,
    device_map="auto",
    # load_in_4bit = True #for lil machines like minegit statu
)

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


@spaces.GPU
def llama_calculator(left_num, operation, right_num) -> str:
    """
    stupid func for asking llama a question and then getting an answer
    inputs:
    - input_question [str]: question for llama to answer
    outputs:
    - response [str]: llama's response
    """

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": str(left_num) + " " + str(operation) + " " + str(right_num),
        },
    ]
    outputs = pipe(messages, max_new_tokens=512)
    response = outputs[0]["generated_text"][-1]["content"]
    return response
