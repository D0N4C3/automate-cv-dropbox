import re
from dataclasses import dataclass

from app.services.cv_parser import candidate_name_from_cv_text
from app.utils.helpers import normalize_name


@dataclass
class NameResult:
    name: str
    confidence: str


BODY_PATTERNS = [
    re.compile(r"(?:my name is|i am)\s+([A-Z][A-Za-z'\-]+(?:\s+[A-Z][A-Za-z'\-]+){1,3})", re.IGNORECASE),
    re.compile(r"^([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})$", re.MULTILINE),
]


def extract_name_from_body(body: str) -> str | None:
    for pattern in BODY_PATTERNS:
        match = pattern.search(body)
        if match:
            return normalize_name(match.group(1))
    return None


def extract_name_from_email_address(email_address: str) -> str | None:
    local = email_address.split("@")[0]
    local = re.sub(r"\d+$", "", local)
    tokens = [t for t in re.split(r"[._-]+", local) if t and len(t) > 1]
    if len(tokens) == 1 and len(tokens[0]) > 5:
        token = tokens[0]
        tokens = [token[: len(token) // 2], token[len(token) // 2 :]]
    if not tokens:
        return None
    return normalize_name(" ".join(tokens[:4]))


def choose_best_name(body: str, email_address: str, cv_text: str) -> NameResult:
    cv_name = normalize_name(candidate_name_from_cv_text(cv_text) or "")
    if cv_name:
        return NameResult(cv_name, "High")

    body_name = extract_name_from_body(body)
    if body_name:
        return NameResult(body_name, "Medium")

    email_name = extract_name_from_email_address(email_address)
    if email_name:
        return NameResult(email_name, "Low")

    return NameResult("Unknown Candidate", "Low")
