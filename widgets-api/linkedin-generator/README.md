# LinkedIn Generator

A Gradio Server-based widget API that converts plain text into LinkedIn-style posts through a model gateway.

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `/health` | Check whether the model gateway is configured and ready |
| `/generate` | Convert plain text into a LinkedIn-style post |

### `/generate`

Transforms a short text prompt into a buzz-worthy LinkedIn post complete with emojis and excitement.

**Input**: `input_text` (string) — the prompt or idea to expand into a LinkedIn post.

**Response**:

```json
{
  "content": "the generated LinkedIn post",
  "model": "model identifier used",
  "usage": {},
  "source_text": "original input prompt"
}
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GATEWAY_URL` | URL of the model gateway service providing LLM inference | (empty — required) |
| `MODEL` | Hugging Face model ID used for text generation | `meta-llama/Llama-3.2-3B-Instruct` |
| `MAX_TOKENS` | Maximum number of tokens in the generated output | `512` |
| `TEMPERATURE` | Sampling temperature controlling output randomness | `0.85` |
| `TOP_P` | Nucleus sampling probability threshold | `0.92` |

## Running Locally

```bash
pip install -r requirements.txt
GATEWAY_URL=<your-gateway-url> python app.py
```

## Deployment

This widget is designed to run as a [Hugging Face Space](https://huggingface.co/spaces) using the Gradio SDK. See `space.yaml` for the space configuration.
