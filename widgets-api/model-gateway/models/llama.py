from typing import Any

import spaces
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline


class LlamaModel:
    _instance: "LlamaModel | None" = None
    _pipe: Any = None

    MODEL_ID: str = "meta-llama/Llama-3.2-3B-Instruct"

    @classmethod
    def get_instance(cls) -> "LlamaModel":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self) -> None:
        if LlamaModel._pipe is not None:
            return

        torch_device = "cuda" if torch.cuda.is_available() else "cpu"
        torch_dtype = (
            torch.bfloat16 if torch_device in ["cuda", "mps"] else torch.float32
        )

        model = AutoModelForCausalLM.from_pretrained(
            self.MODEL_ID,
            torch_dtype=torch_dtype,
            device_map=torch_device,
        )
        tokenizer = AutoTokenizer.from_pretrained(self.MODEL_ID)

        LlamaModel._pipe = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            torch_dtype=torch_dtype,
            device_map="auto",
        )

    @staticmethod
    def get_pipe() -> Any:
        if LlamaModel._pipe is None:
            LlamaModel.get_instance()
        return LlamaModel._pipe

    @staticmethod
    @spaces.GPU
    def generate(
        messages: list[dict[str, str]],
        max_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.9,
        stop: list[str] | None = None,
    ) -> dict[str, Any]:
        pipe = LlamaModel.get_pipe()
        outputs = pipe(
            messages,
            max_new_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            do_sample=temperature > 0,
        )
        content = outputs[0]["generated_text"][-1]["content"]

        prompt_tokens = sum(len(msg["content"].split()) for msg in messages)
        completion_tokens = len(content.split())

        return {
            "model": LlamaModel.MODEL_ID,
            "content": content,
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            },
        }


# Load the model immediately
LlamaModel.get_instance()
print(f"{LlamaModel.MODEL_ID} loaded and ready to generate.")
