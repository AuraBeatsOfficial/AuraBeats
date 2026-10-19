"""
AuraBeats - Formatters
Time, bytes, progress bar, text utilities.
"""

# ---------- duration ----------
def humanize_duration(seconds) -> str:
    """90 -> '1:30'   |   3700 -> '1:01:40'"""
    try:
        seconds = int(seconds)
    except (ValueError, TypeError):
        return "0:00"
    if seconds < 0:
        seconds = 0
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def parse_timestamp(text: str) -> int:
    """'1:30' -> 90   |   '1:02:30' -> 3750   |   '45' -> 45   |   invalid -> -1"""
    if not text:
        return -1
    parts = text.strip().split(":")
    try:
        parts = [int(p) for p in parts]
    except ValueError:
        return -1
    if len(parts) == 1:
        return parts[0]
    if len(parts) == 2:
        return parts[0] * 60 + parts[1]
    if len(parts) == 3:
        return parts[0] * 3600 + parts[1] * 60 + parts[2]
    return -1


# ---------- bytes ----------
def humanize_bytes(n) -> str:
    """1234567 -> '1.18 MB'"""
    try:
        n = float(n)
    except (ValueError, TypeError):
        return "0 B"
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024.0:
            return f"{n:.2f} {unit}" if unit != "B" else f"{int(n)} B"
        n /= 1024.0
    return f"{n:.2f} PB"


# ---------- progress bar ----------
def progress_bar(current, total, size: int = 12,
                 filled: str = "▬", pointer: str = "🔘", empty: str = "▬") -> str:
    """Animated progress bar with pointer."""
    try:
        current = float(current)
        total = float(total)
    except (ValueError, TypeError):
        return (empty * size)
    if total <= 0:
        return (empty * size)
    ratio = max(0.0, min(1.0, current / total))
    pos = int(round(ratio * (size - 1)))
    bar = ""
    for i in range(size):
        if i == pos:
            bar += pointer
        elif i < pos:
            bar += filled
        else:
            bar += empty
    return bar


def progress_line(current, total, size: int = 12) -> str:
    """Full line: bar + times."""
    return f"{progress_bar(current, total, size)}  {humanize_duration(current)}/{humanize_duration(total)}"


# ---------- text ----------
def truncate(text: str, max_len: int = 40, suffix: str = "…") -> str:
    """Safe truncation (unicode friendly)."""
    if not text:
        return ""
    if len(text) <= max_len:
        return text
    return text[: max_len - len(suffix)] + suffix


def escape_md(text: str) -> str:
    """Escape markdown special chars (for Pyrogram legacy md)."""
    if not text:
        return ""
    specials = "_*`[]()~>#+-=|{}.!"
    out = []
    for ch in text:
        if ch in specials:
            out.append("\\" + ch)
        else:
            out.append(ch)
    return "".join(out)


# ---------- numbers ----------
def compact_number(n) -> str:
    """1500 -> '1.5K'   2000000 -> '2.0M'"""
    try:
        n = float(n)
    except (ValueError, TypeError):
        return "0"
    for unit, div in (("B", 1e9), ("M", 1e6), ("K", 1e3)):
        if abs(n) >= div:
            val = n / div
            return f"{val:.1f}{unit}" if val < 10 else f"{int(val)}{unit}"
    return str(int(n))


# ---------- self-test ----------
if __name__ == "__main__":
    tests = [
        ("humanize_duration(0)",        humanize_duration(0)),
        ("humanize_duration(90)",       humanize_duration(90)),
        ("humanize_duration(3700)",     humanize_duration(3700)),
        ("parse_timestamp('1:30')",     parse_timestamp("1:30")),
        ("parse_timestamp('1:02:30')",  parse_timestamp("1:02:30")),
        ("parse_timestamp('bad')",      parse_timestamp("bad")),
        ("humanize_bytes(1024)",        humanize_bytes(1024)),
        ("humanize_bytes(1234567)",     humanize_bytes(1234567)),
        ("compact_number(1500)",        compact_number(1500)),
        ("compact_number(2500000)",     compact_number(2500000)),
        ("truncate('A very long title here', 10)", truncate("A very long title here", 10)),
        ("progress_bar(50, 100, 10)",   progress_bar(50, 100, 10)),
        ("progress_line(30, 60)",       progress_line(30, 60)),
    ]
    for name, val in tests:
        print(f"  {name:<45} -> {val}")
