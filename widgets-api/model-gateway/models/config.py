# Common configuration for all models, including device and dtype settings.

import os
import torch

TOKEN = os.getenv("HF_TOKEN")
QUANTIZE_4_BIT = os.getenv("QUANTIZE_4_BIT", "false").lower() == "true"

torch_device = "cuda" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.bfloat16 if torch_device in ["cuda", "mps"] else torch.float32

print(f"Using {torch_device} with dtype {torch_dtype}...")

model_config = {
    "torch_dtype": torch_dtype,
    "device_map": torch_device,
    "token": TOKEN,
}

tokenizer_config = {
    "token": TOKEN,
}

pipeline_config = {
    "torch_dtype": torch_dtype,
    "device_map": "auto",
}


def enable_quantization():
    print("Enabling 4-bit quantization for compatible models...")
    from transformers import BitsAndBytesConfig

    quantization_config = BitsAndBytesConfig(load_in_4bit=True)
    model_config["quantization_config"] = quantization_config


if QUANTIZE_4_BIT:
    enable_quantization()
