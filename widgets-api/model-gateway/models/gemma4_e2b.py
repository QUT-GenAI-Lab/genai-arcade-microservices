from typing import Any

import torch
from transformers import AutoProcessor, AutoModelForCausalLM, TextStreamer
from . import TextGenerationResult, config, Model, ModelUsage
from .lazy_model import LazyModel

MODEL_ID = Model.GEMMA_4_E2B.id
lazy = LazyModel(MODEL_ID)

processor = None
model = None


@lazy.unload()
def clean_up():
    global processor, model
    del processor
    del model


@lazy.load()
def load():
    global processor, model
    processor = AutoProcessor.from_pretrained(MODEL_ID, **config.tokenizer_config)
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, **config.model_config)


@lazy.entry()
def generate(
    messages: list[dict[str, str]],
    max_tokens: int = 512,
    temperature: float = 0.7,
    top_p: float = 0.9,
    stop: list[str] | None = None,
) -> TextGenerationResult:
    global processor, model
    assert processor is not None, "Processor is not initialized."
    assert model is not None, "Model is not loaded."

    # Process input
    text = processor.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=False,
    )
    inputs = processor(text=text, return_tensors="pt").to(model.device)
    input_len = inputs["input_ids"].shape[-1]

    streamer = TextStreamer(
        processor.tokenizer, skip_prompt=True, skip_special_tokens=True
    )

    with torch.inference_mode():
        outputs = model.generate(  # type: ignore
            **inputs,
            max_new_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            do_sample=temperature > 0,
            streamer=streamer,
        )

    response = processor.decode(outputs[0][input_len:], skip_special_tokens=False)
    content = processor.parse_response(response)
    if isinstance(content, dict) and "content" in content:
        content = content["content"]

    prompt_tokens = len(processor.tokenizer.apply_chat_template(messages))
    completion_tokens = len(
        processor.tokenizer.encode(content, add_special_tokens=False)
    )

    print(
        f"Generation complete. Prompt tokens: {prompt_tokens}, Completion tokens: {completion_tokens}"
    )
    print(f"Generated content: {content}")
    assert type(content) is str, (
        f"Expected generated content to be a string, but got {type(content)}"
    )

    return TextGenerationResult(
        content=content,
        model=MODEL_ID,
        usage=ModelUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
        ),
    )
