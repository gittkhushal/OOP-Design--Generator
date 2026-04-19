"""Parse the AI response into structured sections."""
from __future__ import annotations

import re
from dataclasses import dataclass, field


SECTION_NAMES = ["CLASSES", "ATTRIBUTES", "METHODS", "RELATIONSHIPS", "CODE", "PLANTUML"]


@dataclass
class ParsedDesign:
    classes: list[str] = field(default_factory=list)
    # ClassName -> list of "attr : type"
    attributes: dict[str, list[str]] = field(default_factory=dict)
    # ClassName -> list of "method()"
    methods: dict[str, list[str]] = field(default_factory=dict)
    # list of dicts: {"left", "symbol", "right", "label"}
    relationships: list[dict] = field(default_factory=list)
    code: str = ""
    plantuml: str = ""
    raw: str = ""


_HEADER_RE = re.compile(r"^\s*#{2,4}\s*([A-Z]+)\s*$", re.MULTILINE)
_FENCE_RE = re.compile(r"```([a-zA-Z0-9_+#-]*)\s*\n(.*?)```", re.DOTALL)
_REL_SYMBOLS = ["<|--", "-->", "o--", "*--", "..>"]


def _split_sections(text: str) -> dict[str, str]:
    """Split AI text into a {section_name: body} dict."""
    matches = list(_HEADER_RE.finditer(text))
    out: dict[str, str] = {}
    for i, m in enumerate(matches):
        name = m.group(1).upper()
        if name not in SECTION_NAMES:
            continue
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        out[name] = text[start:end].strip()
    return out


def _strip_fence(body: str) -> str:
    """If body contains a fenced code block, return its inner content; else return body."""
    m = _FENCE_RE.search(body)
    if m:
        return m.group(2).rstrip()
    return body.strip()


def _parse_classes(body: str) -> list[str]:
    out = []
    for line in body.splitlines():
        line = line.strip().lstrip("-*").strip()
        if not line or line.startswith("#"):
            continue
        # accept "ClassName" or "ClassName - description"
        name = re.split(r"[\s:\-]", line, 1)[0].strip()
        if name and re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", name):
            out.append(name)
    # dedupe preserving order
    seen = set()
    deduped = []
    for c in out:
        if c not in seen:
            seen.add(c)
            deduped.append(c)
    return deduped


def _parse_class_blocks(body: str) -> dict[str, list[str]]:
    """Parse blocks shaped like:
    ClassName:
      - item
      - item
    """
    result: dict[str, list[str]] = {}
    current: str | None = None
    for raw in body.splitlines():
        line = raw.rstrip()
        if not line.strip():
            continue
        # detect "ClassName:" header (no leading dash)
        header = re.match(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*:\s*$", line)
        if header:
            current = header.group(1)
            result.setdefault(current, [])
            continue
        # detect bullet item
        item = re.match(r"^\s*[-*]\s*(.+)$", line)
        if item and current is not None:
            result[current].append(item.group(1).strip())
            continue
        # tolerate "ClassName - item" inline
        inline = re.match(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*[-:]\s*(.+)$", line)
        if inline:
            cls, item_text = inline.group(1), inline.group(2)
            result.setdefault(cls, []).append(item_text.strip())
    return result


def _parse_relationships(body: str) -> list[dict]:
    out = []
    for raw in body.splitlines():
        line = raw.strip().lstrip("-*").strip()
        if not line:
            continue
        sym_used = None
        for sym in _REL_SYMBOLS:
            if f" {sym} " in f" {line} ":
                sym_used = sym
                break
        if not sym_used:
            continue
        left, _, rest = line.partition(sym_used)
        right_part, _, label = rest.partition(":")
        out.append(
            {
                "left": left.strip(),
                "symbol": sym_used,
                "right": right_part.strip(),
                "label": label.strip(),
            }
        )
    return out


def parse_response(text: str) -> ParsedDesign:
    sections = _split_sections(text)
    pd = ParsedDesign(raw=text)
    pd.classes = _parse_classes(sections.get("CLASSES", ""))
    pd.attributes = _parse_class_blocks(sections.get("ATTRIBUTES", ""))
    pd.methods = _parse_class_blocks(sections.get("METHODS", ""))
    pd.relationships = _parse_relationships(sections.get("RELATIONSHIPS", ""))
    pd.code = _strip_fence(sections.get("CODE", ""))
    pd.plantuml = _strip_fence(sections.get("PLANTUML", ""))

    # Make sure plantuml has @startuml / @enduml
    if pd.plantuml and "@startuml" not in pd.plantuml:
        pd.plantuml = "@startuml\n" + pd.plantuml
    if pd.plantuml and "@enduml" not in pd.plantuml:
        pd.plantuml = pd.plantuml + "\n@enduml"

    return pd
