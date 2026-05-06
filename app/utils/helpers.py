import re
from typing import Optional


_INTERFACE_RE = re.compile(r"^\s*(?P<interface>I\d+[A-Za-z]?)(?=\D|$)")
_COMPONENT_SUFFIX_RE = re.compile(
    r"\s+(?:\((?P<paren_component>T2/T3|R2/R3|T[123]|R[123])\)|"
    r"(?P<plain_component>T2/T3|R2/R3|T[123]|R[123]))\s*$"
)
_SIDE_SEPARATOR_RE = re.compile(r"\s-\s*")
_TRAILING_PARENTHESES_RE = re.compile(r"\s*\([^)]*\)\s*$")


def extract_interface_name(column_name: object) -> Optional[str]:
    """Return the leading interface id from a PLD channel label."""
    match = _INTERFACE_RE.match(str(column_name or ""))
    if match is None:
        return None
    return match.group("interface")


def extract_part_side(column_name: object) -> Optional[str]:
    """Return the part-side name from a PLD channel label.

    Labels can include a coordinate-system block before the component suffix,
    for example ``I1 - SIDE (CS-8012) T1``, or omit it as ``I1 - SIDE T1``.
    Older exports may also place the component itself in parentheses.
    """
    text = str(column_name or "").strip()
    if not text or text.startswith("Phase_") or extract_interface_name(text) is None:
        return None

    component_match = _COMPONENT_SUFFIX_RE.search(text)
    if component_match is None:
        return None

    label_without_component = text[: component_match.start()].strip()
    label_without_component = _TRAILING_PARENTHESES_RE.sub("", label_without_component).strip()

    separator_matches = list(_SIDE_SEPARATOR_RE.finditer(label_without_component))
    if separator_matches:
        side_start = separator_matches[-1].end()
        side = label_without_component[side_start:].strip()
    else:
        interface_match = _INTERFACE_RE.match(label_without_component)
        if interface_match is None:
            return None
        remainder = label_without_component[interface_match.end() :].strip()
        if not remainder.startswith("-"):
            return None
        side = remainder[1:].strip()

    return side or None
