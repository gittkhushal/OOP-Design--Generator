"""Encode PlantUML source for the public PlantUML server, with Kroki fallback.

Reference for the PlantUML encoding:
  https://plantuml.com/text-encoding
It is deflate (raw, no zlib header) followed by a custom base64-like alphabet.

Kroki uses standard zlib + URL-safe base64.
"""
from __future__ import annotations

import base64
import zlib
import requests


_PLANTUML_ALPHABET = (
    "0123456789"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "abcdefghijklmnopqrstuvwxyz"
    "-_"
)


def _encode6bit(b: int) -> str:
    return _PLANTUML_ALPHABET[b & 0x3F]


def _append_3bytes(b1: int, b2: int, b3: int) -> str:
    c1 = b1 >> 2
    c2 = ((b1 & 0x3) << 4) | (b2 >> 4)
    c3 = ((b2 & 0xF) << 2) | (b3 >> 6)
    c4 = b3 & 0x3F
    return _encode6bit(c1) + _encode6bit(c2) + _encode6bit(c3) + _encode6bit(c4)


def plantuml_encode(text: str) -> str:
    """Encode PlantUML source into the URL-safe form used by plantuml.com."""
    data = text.encode("utf-8")
    # raw deflate (no zlib header / checksum)
    compressor = zlib.compressobj(9, zlib.DEFLATED, -zlib.MAX_WBITS)
    compressed = compressor.compress(data) + compressor.flush()

    res = []
    i = 0
    while i < len(compressed):
        b1 = compressed[i]
        b2 = compressed[i + 1] if i + 1 < len(compressed) else 0
        b3 = compressed[i + 2] if i + 2 < len(compressed) else 0
        res.append(_append_3bytes(b1, b2, b3))
        i += 3
    return "".join(res)


def kroki_encode(text: str) -> str:
    """Encode PlantUML source for Kroki (zlib + URL-safe base64, no padding)."""
    compressed = zlib.compress(text.encode("utf-8"), 9)
    return base64.urlsafe_b64encode(compressed).decode("ascii").rstrip("=")


def build_urls(plantuml_source: str, fmt: str = "svg") -> dict:
    """Return primary and fallback diagram URLs."""
    primary = f"https://www.plantuml.com/plantuml/{fmt}/{plantuml_encode(plantuml_source)}"
    fallback = f"https://kroki.io/plantuml/{fmt}/{kroki_encode(plantuml_source)}"
    return {"primary": primary, "fallback": fallback}


def _probe(url: str, timeout: int) -> bool:
    """Return True if the server returns a 2xx for this URL.
    Uses a tiny ranged GET because some servers (e.g. Kroki) reject HEAD."""
    try:
        r = requests.get(
            url, timeout=timeout, stream=True, headers={"Range": "bytes=0-0"}
        )
        r.close()
        return 200 <= r.status_code < 400
    except requests.RequestException:
        return False


def pick_working_url(plantuml_source: str, fmt: str = "svg", timeout: int = 8) -> dict:
    """Probe the primary URL; fall back to Kroki if it fails."""
    urls = build_urls(plantuml_source, fmt=fmt)
    chosen = urls["primary"] if _probe(urls["primary"], timeout) else urls["fallback"]
    return {"chosen": chosen, **urls}
