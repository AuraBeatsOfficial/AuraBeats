"""AuraBeats - Player card / Now-playing text composer."""
from utils.formatters import (
    humanize_duration, progress_bar, compact_number, truncate,
)

BAR_SIZE = 12


def now_playing(track: dict, position: int = 0, paused: bool = False) -> str:
    """Compose a premium now-playing card."""
    title    = truncate(track.get("title", "Unknown"), 55)
    duration = int(track.get("duration", 0) or 0)
    requester = track.get("requester", "—")
    uploader = track.get("uploader", "")
    views    = compact_number(track.get("views", 0)) if track.get("views") else "—"

    status = "⏸ **Paused**" if paused else "▶️ **Playing**"
    bar = progress_bar(position, duration, BAR_SIZE)
    time_line = f"`{humanize_duration(position)} / {humanize_duration(duration)}`"

    lines = [
        f"🎶 **Now Playing**",
        "",
        f"**{title}**",
        "",
        f"`{bar}`",
        f"{time_line}",
        "",
        f"👤 **Requested by:** {requester}",
    ]
    if uploader:
        lines.append(f"🎙 **Uploader:** {uploader}")
    if views != "—":
        lines.append(f"👁 **Views:** {views}")
    lines.append(f"🎧 **Status:** {status}")
    return "\n".join(lines)


def queued(track: dict, position: int) -> str:
    """Compose a 'queued' card."""
    title = truncate(track.get("title", "Unknown"), 55)
    dur = humanize_duration(track.get("duration", 0))
    return (
        f"➕ **Queued at #{position}**\n\n"
        f"🎵 **{title}**\n"
        f"⏱ `{dur}`\n"
        f"👤 {track.get('requester', '—')}"
    )


def queue_card(queue: list, current: dict | None = None) -> str:
    """Compose queue view."""
    lines = []
    if current:
        lines.append(f"**▶️ Now:** {truncate(current.get('title','?'), 40)}")
        lines.append("")
    if not queue:
        lines.append("📭 Queue is empty.")
        return "\n".join(lines)
    lines.append(f"**📋 Up Next ({len(queue)})**")
    for i, t in enumerate(queue[:15], 1):
        lines.append(
            f"`{i}.` {truncate(t.get('title','?'), 35)} "
            f"`{humanize_duration(t.get('duration', 0))}`"
        )
    if len(queue) > 15:
        lines.append(f"_…and {len(queue)-15} more_")
    return "\n".join(lines)


def search_result(track: dict) -> str:
    """Compose search result message."""
    title = truncate(track.get("title", "Unknown"), 60)
    return (
        f"✅ **Found**\n\n"
        f"🎵 **{title}**\n"
        f"⏱ `{humanize_duration(track.get('duration', 0))}`\n"
        f"🎙 {track.get('uploader', '—')}\n"
        f"👁 {compact_number(track.get('views', 0))}"
    )
