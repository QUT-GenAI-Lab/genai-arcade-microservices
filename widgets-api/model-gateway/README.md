# Model Gateway API

Unified Gradio API for serving LLMs. Supports text generation across multiple models through a single endpoint.

## Usage

Install the client:

```bash
pip install gradio_client
```

### Connect

```python
from gradio_client import Client

# Hosted Space
client = Client("qut-genailab/model-gateway-api")

# Local server
client = Client("http://localhost:7860")
```

### List models

```python
result = client.predict(api_name="/models")
for model in result["models"]:
    print(f"{model['id']} ({model['max_tokens']} max tokens)")
```

### Generate text

```python
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Explain quantum computing in one sentence."},
]

result = client.predict(
    messages=messages,
    model="google/gemma-4-E2B-it",
    max_tokens=256,
    temperature=0.7,
    api_name="/generate",
)

print(result["content"])
print(f"Tokens: {result['usage']['prompt_tokens']} prompt + {result['usage']['completion_tokens']} completion")
```

### Asynchronous generation

```python
job = client.submit(messages=messages, api_name="/generate")
# ... do other work ...
result = job.result()
print(result["content"])
```

### Using default parameters

All parameters except `messages` have defaults, so a minimal call looks like:

```python
result = client.predict(
    messages=[{"role": "user", "content": "Hello!"}],
    api_name="/generate",
)
```


## Available Models

| Model ID | Type | Backend | Max Tokens |
|---|---|---|---|
| `meta-llama/Llama-3.2-3B-Instruct` | text-generation | local | 4096 |
| `google/gemma-4-E2B-it` | text-generation | local | 4096 |

## API Endpoints

### `/generate`

Text generation using a chat template.

**Parameters:**

| Name | Type | Default | Description |
|---|---|---|---|
| `messages` | `list[dict[str, str]]` | (required) | Chat messages with `role` and `content` keys |
| `model` | `str` | `google/gemma-4-E2B-it` | Model ID to use for generation |
| `max_tokens` | `int` | `512` | Maximum tokens to generate |
| `temperature` | `float` | `0.7` | Sampling temperature |
| `top_p` | `float` | `0.9` | Nucleus sampling threshold |
| `stop` | `list[str]` | `None` | Stop sequences |

**Returns:**

```json
{
    "model": "google/gemma-4-E2B-it",
    "content": "Generated text...",
    "usage": {
        "prompt_tokens": 42,
        "completion_tokens": 128,
        "total_tokens": 170
    }
}
```

### `/models`

List available models and their capabilities.

**Returns:**

```json
{
    "models": [
        {
            "id": "meta-llama/Llama-3.2-3B-Instruct",
            "type": "text-generation",
            "backend": "local",
            "max_tokens": 4096
        },
        {
            "id": "google/gemma-4-E2B-it",
            "type": "text-generation",
            "backend": "local",
            "max_tokens": 4096
        }
    ]
}
```


## Development Workflow

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables** for gated model access and optional features:

   ```bash
   $env:HF_TOKEN = "your-huggingface-token"
   $env:LAZY_LOAD = "true"        # Load models on first request instead of at startup
   $env:QUANTIZE_4_BIT = "true"   # Enable 4-bit quantization for compatible models
   ```

3. Run the server:

   ```bash
   python app.py
   ```

   This starts a Gradio Server at **http://localhost:7860**.

4. Connect with the client:

   ```python
   from gradio_client import Client
   client = Client("http://localhost:7860")
   ```

## Deployment

Configured as a Hugging Face Space via `space.yaml`. The Space ID is `qut-genailab/model-gateway-api`.
