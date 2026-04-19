"""OpenAI-compatible chat completion client."""
from __future__ import annotations

import os
import requests


class AIClientError(RuntimeError):
    pass


def call_ai(prompt: str, *, system: str | None = None, timeout: int = 120) -> str:
    """Call an OpenAI-compatible /chat/completions endpoint and return text."""
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

    if not api_key:
        raise AIClientError(
            "OPENAI_API_KEY is not set. Copy .env.example to .env and add your key."
        )

    url = f"{base_url}/chat/completions"
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.2,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=timeout)
    except requests.RequestException as e:
        raise AIClientError(f"Network error calling AI provider: {e}") from e

    if resp.status_code != 200:
        raise AIClientError(
            f"AI provider returned {resp.status_code}: {resp.text[:500]}"
        )

    data = resp.json()
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as e:
        raise AIClientError(f"Unexpected AI response shape: {data}") from e
