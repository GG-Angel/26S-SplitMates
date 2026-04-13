from datetime import datetime, timezone


def parse_mysql_datetime(dt_string: str) -> datetime:
    for fmt in (
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
        "%a, %d %b %Y %H:%M:%S %Z",
    ):
        try:
            return datetime.strptime(dt_string.strip(), fmt)
        except ValueError:
            continue
    raise ValueError(f"Unable to parse MySQL datetime string: '{dt_string}'")


def time_relative(dt: datetime, now: datetime | None = None) -> str:
    if now is None:
        now = datetime.utcnow() if dt.tzinfo is None else datetime.now(timezone.utc)

    delta = (dt - now).total_seconds()
    past = delta < 0
    s = abs(delta)

    if s < 45:
        value, unit = None, None
    elif s < 2700:
        value, unit = round(s / 60), "minute"
    elif s < 79200:
        value, unit = round(s / 3600), "hour"
    elif s < 554400:
        value, unit = round(s / 86400), "day"
    elif s < 2160000:
        value, unit = round(s / 604800), "week"
    elif s < 31536000:
        value, unit = round(s / 2592000), "month"
    else:
        value, unit = round(s / 31536000), "year"

    if value is None:
        return "Just now"
    label = f"{value} {unit}{'s' if value != 1 else ''}"
    return f"{label} ago" if past else f"In {label}"


def format_date(dt: datetime) -> str:
    return dt.strftime("%B %-d, %Y")


def format_time(dt: datetime) -> str:
    return dt.strftime("%-I:%M %p")

def is_past_date(dt: datetime) -> bool:
    return dt < datetime.now()


def highlight_color(color: str, content: str) -> str:
    return f":{color}[{content}]"
