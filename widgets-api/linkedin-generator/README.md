# LinkedIn Generator

A Gradio Server-based widget API that converts plain text into LinkedIn-style posts through the model gateway.

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
  "source_text": "original input prompt"
}
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GATEWAY_URL` | URL of the model gateway service providing LLM inference | `https://inference.genai-arcade.net` |
| `GATEWAY_API_KEY` | API key for the model gateway (`x-api-key` header) | (required) |
| `MODEL` | Bedrock model ID used for text generation. Must be one of: `amazon.nova-micro-v1:0`, `google.gemma-3-4b-it`, `openai.gpt-oss-20b-1:0`, `deepseek.v3-v1:0` | `amazon.nova-micro-v1:0` |

## Generating the API Client

The widget talks to the model gateway through a Python client generated from its
OpenAPI spec using
[`openapi-python-client`](https://github.com/openapi-generators/openapi-python-client).
The generated package lives in `inference_gateway_client/` at the widget root and
**is committed to the repo** — a fresh `pip install -r requirements.txt` is enough
to use it.

To regenerate the client (e.g. after the gateway's OpenAPI spec changes), install
`openapi-python-client` with `pipx` or `uv tool` and run:

```bash
pipx run --spec openapi-python-client openapi-python-client generate \
  --url https://docs.inference.genai-arcade.net/swagger.json \
  --output-path inference_gateway_client \
  --config openapi-python-client.yaml \
  --overwrite
```

or, with `uv`:

```bash
uv tool run --from openapi-python-client openapi-python-client generate \
  --url https://docs.inference.genai-arcade.net/swagger.json \
  --output-path inference_gateway_client \
  --config openapi-python-client.yaml \
  --overwrite
```

`openapi-python-client` is a developer-time tool only; it is not added to
`requirements.txt`.

## Running Locally

```bash
pip install -r requirements.txt
GATEWAY_API_KEY=<your-gateway-api-key> python app.py
```

To target a non-default gateway (e.g. a local stack), also set `GATEWAY_URL`:

```bash
GATEWAY_URL=http://localhost:8787 GATEWAY_API_KEY=<your-gateway-api-key> python app.py
```

On Windows, use `set` instead of prefixing environment variables:

```bash
set GATEWAY_API_KEY=<your-gateway-api-key>
python app.py
```

## Deployment

This widget is designed to run as a [Hugging Face Space](https://huggingface.co/spaces) using the Gradio SDK. See `space.yaml` for the space configuration.
