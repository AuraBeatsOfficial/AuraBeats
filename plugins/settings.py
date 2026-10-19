"""AuraBeats - /settings per-chat configuration panel."""
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery

from config import PREFIXES
from core.settings import get_all, set as set_setting, reset
from utils.decorators import require_admin
from utils.keyboard import settings_panel


@Client.on_message(filters.command("settings", PREFIXES) & filters.group)
@require_admin
async def settings_cmd(client, message: Message):
    s = await get_all(message.chat.id)
    text = (
        f"⚙️ **{message.chat.title} — Settings**\n\n"
        f"🔊 **Volume:** `{s.get('volume', 100)}%`\n"
        f"🔁 **Loop:** `{s.get('loop', 'off')}`\n"
        f"🎚 **Effects:** `{'enabled' if s.get('feature_effects') else 'disabled'}`\n"
        f"🧠 **AI:** `{'enabled' if s.get('feature_ai') else 'disabled'}`\n"
        f"🌐 **Language:** `{s.get('language', 'en')}`\n"
    )
    await message.reply_text(text, reply_markup=settings_panel(s))


@Client.on_message(filters.command("resetsettings", PREFIXES) & filters.group)
@require_admin
async def reset_cmd(client, message: Message):
    await reset(message.chat.id)
    await message.reply_text("♻️ **Settings reset to defaults.**")


# Settings button handlers (cb:set:*)
@Client.on_callback_query(filters.regex(r"^cb:set:"))
async def settings_cb(client, q: CallbackQuery):
    chat_id = q.message.chat.id
    key = q.data.split(":", 2)[-1]

    if key == "volume":
        s = await get_all(chat_id)
        cur = s.get("volume", 100)
        # cycle: 50 -> 75 -> 100 -> 125 -> 150 -> 200 -> 50
        cycle = [50, 75, 100, 125, 150, 200]
        try:
            idx = cycle.index(cur)
            nxt = cycle[(idx + 1) % len(cycle)]
        except ValueError:
            nxt = 100
        await set_setting(chat_id, "volume", nxt)
        await q.answer(f"Volume: {nxt}%")

    elif key == "loop":
        s = await get_all(chat_id)
        cur = s.get("loop", "off")
        nxt = {"off": "song", "song": "queue", "queue": "off"}.get(cur, "off")
        await set_setting(chat_id, "loop", nxt)
        await q.answer(f"Loop: {nxt}")

    elif key == "effects":
        s = await get_all(chat_id)
        cur = s.get("feature_effects", True)
        await set_setting(chat_id, "feature_effects", not cur)
        await q.answer(f"Effects: {'OFF' if cur else 'ON'}")

    elif key == "ai":
        s = await get_all(chat_id)
        cur = s.get("feature_ai", True)
        await set_setting(chat_id, "feature_ai", not cur)
        await q.answer(f"AI: {'OFF' if cur else 'ON'}")

    # refresh panel
    s = await get_all(chat_id)
    try:
        await q.message.edit_reply_markup(settings_panel(s))
    except Exception:
        pass
