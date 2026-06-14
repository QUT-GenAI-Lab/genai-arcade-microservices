import os
from datetime import UTC, datetime
from typing import Any

import httpx

from inference_gateway_api_client import AuthenticatedClient
from inference_gateway_api_client.api.default import (
    get_health,
    post_generate_chat,
)
from inference_gateway_api_client.errors import UnexpectedStatus
from inference_gateway_api_client.models import (
    PostGenerateChatBody,
    PostGenerateChatBodyMessagesItem,
    PostGenerateChatBodyModel,
)
from inference_gateway_api_client.models.post_generate_chat_body_messages_item_role import (
    PostGenerateChatBodyMessagesItemRole,
)

GATEWAY_URL = os.getenv("GATEWAY_URL", "https://inference.genai-arcade.net").strip()
DEFAULT_MODEL = PostGenerateChatBodyModel.AMAZON_NOVA_MICRO_V10
API_KEY = os.getenv("GATEWAY_API_KEY", "").strip()

SYSTEM_PROMPT = """You are now a LinkedIn post generator. I will just give you a fraction of an idea and you will convert it into a buzzing LinkedIn post full of emojis and excitement, just like every other LinkedIn post. Give me one post without any explanation."""


def get_client() -> AuthenticatedClient:
    return AuthenticatedClient(
        base_url=GATEWAY_URL,
        headers={"x-api-key": API_KEY},
        timeout=httpx.Timeout(60.0),
        raise_on_unexpected_status=True,
        token=API_KEY,
    )


# TODO: This function will likely be repeated across all widgets, so consider moving it to a shared utility module.
def check_health() -> dict[str, Any]:
    if not API_KEY:
        raise ValueError("GATEWAY_API_KEY is required.")

    metadata: dict[str, Any] = {
        "checked_at": datetime.now(UTC).isoformat(),
        "gateway_url": GATEWAY_URL,
        "endpoint": "/health",
        "http_status": None,
        "error": None,
    }

    try:
        with get_client() as client:
            response = get_health.sync_detailed(client=client)

        metadata["http_status"] = int(response.status_code)

        if response.parsed is None:
            raise RuntimeError(
                f"Gateway returned an empty response body (status {metadata['http_status']})."
            )

        if response.parsed.status.value != "ok":
            metadata["error"] = f"Unexpected status: {response.parsed.status.value}"
            return {
                "status": "error",
                "message": "Model gateway reported a non-healthy status.",
                "metadata": metadata,
            }

        print(
            f"Model gateway health check successful (http_status={metadata['http_status']})."
        )
        return {
            "status": "success",
            "message": "Model gateway is ready.",
            "metadata": metadata,
        }
    except UnexpectedStatus as error:
        metadata["http_status"] = error.status_code
        metadata["error"] = str(error)
        return {
            "status": "error",
            "message": "Model gateway health check failed.",
            "metadata": metadata,
        }
    except Exception as error:
        metadata["error"] = str(error)
        return {
            "status": "error",
            "message": "Model gateway health check failed.",
            "metadata": metadata,
        }


def generate_linkedin_post(input_text: str) -> dict[str, Any]:
    prompt = input_text.strip()
    if not prompt:
        raise ValueError("input_text must not be empty.")

    if not API_KEY:
        raise ValueError("GATEWAY_API_KEY is required.")

    body = PostGenerateChatBody(
        messages=[
            PostGenerateChatBodyMessagesItem(
                role=PostGenerateChatBodyMessagesItemRole.USER,
                content=prompt,
            )
        ],
        system=SYSTEM_PROMPT,
        model=PostGenerateChatBodyModel(os.getenv("MODEL", DEFAULT_MODEL.value)),
    )

    try:
        with get_client() as client:
            response = post_generate_chat.sync_detailed(client=client, body=body)
    except Exception as error:
        raise RuntimeError(f"Gateway request failed: {error}") from error

    http_status = int(response.status_code)
    if http_status >= 400 or response.parsed is None:
        raise RuntimeError(
            f"Gateway returned status {http_status}: "
            f"{response.content.decode(errors='ignore')}"
        )

    print(f"Gateway request successful (http_status={http_status}).")
    return {"content": response.parsed.content, "source_text": prompt}


__all__ = ["check_health", "generate_linkedin_post"]
