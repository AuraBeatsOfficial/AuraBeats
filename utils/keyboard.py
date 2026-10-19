"""AuraBeats - Inline keyboard builders."""
from pyrogram.types import InlineKeyboardButton as Btn, InlineKeyboardMarkup as Kb


def player(paused: bool = False) -> Kb:
    """Main player controls."""
    play_pause = ("▶️ Resume", "cb:resume") if paused else ("⏸ Pause", "cb:pause")
    return Kb([
        [Btn(play_pause[0], callback_data=play_pause[1]),
         Btn("⏭ Skip", callback_data="cb:skip"),
         Btn("⏹ Stop", callback_data="cb:stop")],
        [Btn("🎚 Effects", callback_data="cb:eq_menu"),
         Btn("🔀 Shuffle", callback_data="cb:shuffle")],
        [Btn("🔁 Loop", callback_data="cb:loop"),
         Btn("📋 Queue", callback_data="cb:queue"),
         Btn("❌ Close", callback_data="cb:close")],
    ])


def queue_page(items: list, page: int = 0, per_page: int = 8) -> Kb:
    total_pages = max(1, (len(items) + per_page - 1) // per_page)
    page = max(0, min(page, total_pages - 1))
    start = page * per_page
    rows = []
    for i, track in enumerate(items[start:start + per_page], start + 1):
        title = track.get("title", "Unknown")[:30]
        rows.append([Btn(f"{i}. {title}", callback_data=f"cb:track:{i-1}")])
    nav = []
    if page > 0:
        nav.append(Btn("⬅️", callback_data=f"cb:qpage:{page-1}"))
    nav.append(Btn(f"{page+1}/{total_pages}", callback_data="cb:noop"))
    if page < total_pages - 1:
        nav.append(Btn("➡️", callback_data=f"cb:qpage:{page+1}"))
    if nav:
        rows.append(nav)
    return Kb(rows)


def eq_menu() -> Kb:
    presets = ["flat", "bass", "treble", "vocal", "nightcore",
               "slowed", "lofi", "8d", "3d", "acoustic", "clear"]
    rows, row = [], []
    for p in presets:
        row.append(Btn(p.title(), callback_data=f"cb:eq:{p}"))
        if len(row) == 3:
            rows.append(row); row = []
    if row:
        rows.append(row)
    rows.append([Btn("⬅️ Back", callback_data="cb:back_player")])
    return Kb(rows)


def confirm(action: str, data: str = "") -> Kb:
    return Kb([[
        Btn("✅ Yes", callback_data=f"cb:confirm:{action}:{data}"),
        Btn("❌ No", callback_data="cb:close"),
    ]])


def start_menu(bot_username: str) -> Kb:
    return Kb([
        [Btn("➕ Add to Group", url=f"https://t.me/{bot_username}?startgroup=true")],
        [Btn("📖 Help", callback_data="cb:help"),
         Btn("📢 Updates", url="https://t.me/Vip_Sakil_Bio")],
        [Btn("👤 Developer", url="https://t.me/YO_UR_OFFICIAL_CRUSH")],
    ])


def settings_panel(chat_settings: dict) -> Kb:
    def tag(key, on_off=True):
        v = chat_settings.get(key)
        if on_off:
            return "✅" if v else "❌"
        return str(v)
    return Kb([
        [Btn(f"🔊 Volume: {chat_settings.get('volume', 100)}%",
             callback_data="cb:set:volume")],
        [Btn(f"🔁 Loop: {chat_settings.get('loop', 'off')}",
             callback_data="cb:set:loop")],
        [Btn(f"🎚 Effects {tag('feature_effects')}",
             callback_data="cb:set:effects"),
         Btn(f"🧠 AI {tag('feature_ai')}",
             callback_data="cb:set:ai")],
        [Btn("❌ Close", callback_data="cb:close")],
    ])
