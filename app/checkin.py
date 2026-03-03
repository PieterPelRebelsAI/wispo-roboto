from dataclasses import dataclass
from datetime import datetime, timezone

from app.mother_of_all_file import get_name

EXPIRY_HOURS = 4

_checkins: dict[int, "CheckIn"] = {}


@dataclass
class CheckIn:
    user_name: str
    user_id: int
    location: str
    group_size: int
    timestamp: datetime


def _parse_checkin_text(text: str) -> tuple[str, int]:
    raw = text.split(maxsplit=1)
    if len(raw) < 2:
        return "", 1

    body = raw[1].strip()
    last_comma = body.rfind(",")
    if last_comma == -1:
        return body, 1

    after_comma = body[last_comma + 1 :].strip()
    if after_comma.isdigit():
        return body[:last_comma].strip(), int(after_comma)

    return body, 1


def _relative_time(dt: datetime) -> str:
    now = datetime.now(timezone.utc)
    diff = now - dt
    minutes = int(diff.total_seconds() // 60)

    if minutes < 1:
        return "just now"
    if minutes < 60:
        return f"{minutes} min ago"

    hours = minutes // 60
    return f"{hours}h ago"


def add_checkin(message: dict) -> str:
    text = message.get("text", "")
    location, group_size = _parse_checkin_text(text)

    if not location:
        return "Where are you? Usage: /checkin Bauer's Schi-Alm, 4"

    user_name = get_name(message)
    user_id = message["from"]["id"]

    _checkins[user_id] = CheckIn(
        user_name=user_name,
        user_id=user_id,
        location=location,
        group_size=group_size,
        timestamp=datetime.now(timezone.utc),
    )

    if group_size > 1:
        return f"Checked in! {user_name} + {group_size - 1} others @ {location}"
    return f"Checked in! {user_name} @ {location}"


def get_active_checkins() -> str:
    now = datetime.now(timezone.utc)
    expired = [
        uid
        for uid, ci in _checkins.items()
        if (now - ci.timestamp).total_seconds() > EXPIRY_HOURS * 3600
    ]
    for uid in expired:
        del _checkins[uid]

    if not _checkins:
        return "Nobody has checked in yet. Be the first! /checkin <location>"

    lines = ["*Where is everyone?*\n"]
    for ci in sorted(_checkins.values(), key=lambda c: c.timestamp, reverse=True):
        time_ago = _relative_time(ci.timestamp)
        if ci.group_size > 1:
            lines.append(f"- {ci.user_name} + {ci.group_size - 1} others @ {ci.location} ({time_ago})")
        else:
            lines.append(f"- {ci.user_name} @ {ci.location} ({time_ago})")

    return "\n".join(lines)
