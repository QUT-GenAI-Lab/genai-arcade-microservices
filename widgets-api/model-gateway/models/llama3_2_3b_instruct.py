from typing import Any

from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline, TextStreamer
from . import config, Model
from .lazy_model import LazyModel

MODEL_ID = Model.LLAMA_3_2_3B_INSTRUCT.model_id
lazy = LazyModel(MODEL_ID)

model = None
tokenizer = None
pipe = None


@lazy.unload()
def clean_up():
    global model, tokenizer, pipe
    del model
    del tokenizer
    del pipe


@lazy.load()
def init():
    global model, tokenizer, pipe
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, **config.model_config)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, **config.tokenizer_config)

    pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        **config.pipeline_config,
    )


@lazy.entry()
def generate(
    messages: list[dict[str, str]],
    max_tokens: int = 512,
    temperature: float = 0.7,
    top_p: float = 0.9,
    stop: list[str] | None = None,
) -> dict[str, Any]:
    global model, tokenizer, pipe
    assert pipe is not None, "Pipeline is not initialized."
    assert pipe.tokenizer is not None, "Tokenizer is not loaded."

    print(f"Generating with {MODEL_ID}...")
    streamer = TextStreamer(pipe.tokenizer, skip_prompt=True, skip_special_tokens=True)
    outputs = pipe(
        messages,
        max_new_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
        do_sample=temperature > 0,
        # Enable streaming output to console
        streamer=streamer,
    )
    content = outputs[0]["generated_text"][-1]["content"]

    prompt_tokens = len(pipe.tokenizer.apply_chat_template(messages))
    completion_tokens = len(pipe.tokenizer.encode(content, add_special_tokens=False))

    print(
        f"Generation complete. Prompt tokens: {prompt_tokens}, Completion tokens: {completion_tokens}"
    )
    print(f"Generated content: {content}")

    return {
        "model": MODEL_ID,
        "content": content,
        "usage": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
        },
    }
