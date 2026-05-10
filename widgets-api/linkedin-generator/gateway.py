from datetime import UTC, datetime
from typing import Any

from gradio_client import Client

from config import get_settings

_gateway_client: Client | None = None
_gateway_client_url: str | None = None


def _get_gateway_client() -> Client:
    global _gateway_client, _gateway_client_url

    url = get_settings().gateway_url
    if not url:
        raise RuntimeError("GATEWAY_URL is not configured.")

    if _gateway_client is None or _gateway_client_url != url:
        _gateway_client = Client(url)
        _gateway_client_url = url

    return _gateway_client


def reset_client() -> None:
    global _gateway_client, _gateway_client_url
    _gateway_client = None
    _gateway_client_url = None


def _first_payload(result: Any) -> Any:
    if isinstance(result, dict) and "data" in result:
        data = result["data"]
        if isinstance(data, list) and data:
            return data[0]
        return data

    if isinstance(result, (list, tuple)) and result:
        return result[0]

    return result


def _extract_models(result: Any) -> list[dict[str, Any]]:
    payload = _first_payload(result)

    if isinstance(payload, dict):
        models = payload.get("models", [])
        if isinstance(models, list):
            return [model for model in models if isinstance(model, dict)]

    return []


def _extract_generation(result: Any, fallback_model: str) -> dict[str, Any]:
    payload = _first_payload(result)

    if isinstance(payload, dict):
        content = payload.get("content", "")
        return {
            "content": content if isinstance(content, str) else str(content),
            "model": payload.get("model", fallback_model),
            "usage": payload.get("usage", {}),
        }

    if isinstance(payload, str):
        return {"content": payload, "model": fallback_model, "usage": {}}

    return {"content": str(payload), "model": fallback_model, "usage": {}}


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def check_gateway_health() -> dict[str, Any]:
    settings = get_settings()
    url = settings.gateway_url
    print(f"Checking model gateway health at URL: {url or 'Not Configured'}")
    metadata: dict[str, Any] = {
        "checked_at": _now_iso(),
        "gateway_url": url or None,
        "endpoint": "/models",
    }

    try:
        models = list_models()
        metadata["model_count"] = len(models)
        metadata["models"] = [model.get("id") for model in models if model.get("id")]

        print(
            f"Model gateway health check successful. Found {len(models)} models: {metadata['models']}"
        )

        return {
            "status": "success",
            "message": "Model gateway is ready.",
            "metadata": metadata,
        }
    except Exception as error:
        reset_client()
        metadata["error"] = str(error)
        return {
            "status": "error",
            "message": "Model gateway health check failed.",
            "metadata": metadata,
        }


def list_models() -> list[dict[str, Any]]:
    result = _get_gateway_client().predict(api_name="/models")
    return _extract_models(result)


def generate(
    messages: list[dict[str, str]],
    model: str | None = None,
    max_tokens: int | None = None,
    temperature: float | None = None,
    top_p: float | None = None,
    stop: list[str] | None = None,
) -> dict[str, Any]:
    settings = get_settings()
    model = model or settings.model
    max_tokens = max_tokens if max_tokens is not None else settings.max_tokens
    temperature = temperature if temperature is not None else settings.temperature
    top_p = top_p if top_p is not None else settings.top_p

    result = _get_gateway_client().predict(
        messages=messages,
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
        stop=stop,
        api_name="/generate",
    )
    return _extract_generation(result, fallback_model=model)
