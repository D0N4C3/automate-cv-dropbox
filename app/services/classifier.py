from dataclasses import dataclass


@dataclass(frozen=True)
class RoleConfig:
    role: str
    keywords: tuple[str, ...]


ROLE_RULES = (
    RoleConfig("Battery Expert", ("battery", "lithium", "lithium-ion", "li-ion", "expert")),
    RoleConfig("Sales & Marketing", ("sales", "marketing")),
)


def classify_role(subject: str, body: str) -> str | None:
    text = f"{subject} {body}".lower()
    for rule in ROLE_RULES:
        if any(keyword in text for keyword in rule.keywords):
            return rule.role
    return None
