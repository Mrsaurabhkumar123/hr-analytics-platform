"""Small, dependency-free input validation helpers used across routes."""
import re

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def is_valid_email(value: str) -> bool:
    return bool(value) and bool(EMAIL_RE.match(value))


def is_strong_password(value: str) -> bool:
    """Require 8+ chars with at least one letter and one digit."""
    if not value or len(value) < 8:
        return False
    return bool(re.search(r"[A-Za-z]", value)) and bool(re.search(r"\d", value))


def paginate_args(request, default_page=1, default_per_page=20, max_per_page=100):
    try:
        page = max(int(request.args.get("page", default_page)), 1)
    except (TypeError, ValueError):
        page = default_page
    try:
        per_page = int(request.args.get("per_page", default_per_page))
    except (TypeError, ValueError):
        per_page = default_per_page
    per_page = min(max(per_page, 1), max_per_page)
    return page, per_page
