"""AuraBeats - /queue /nowplaying /qclear /qjump /shuffle /loop."""
from pyrogram import Client, filters
from pyrogram.types import Message

from config import PREFIXES
from core.calls import active_chats, queues, paused
from core.settings import get, set as set_setting
from utils.decorators import require_assistant
from utils.inline_ui import queue_card, now_playing
from utils.keyboard import player, queue_page


@Client.on_message(filters.command("queue", PREFIXES) & filters.group)
async def queue_cmd(client, message: Message):
    chat_id = message.chat.id
    q = queues.get(chat_id, [])
    cur = active_chats.get(chat_id)
    if not q and not cur:
        return await message.reply_text("📭 **Queue is empty.**")
    await message.reply_text(
        queue_card(q, cur),
        reply_markup=queue_page(q, 0) if q else None,
    )


@Client.on_message(filters.command(["nowplaying", "np", "current"], PREFIXES) & filters.group)
async def np_cmd(client, message: Message):
    cur = active_chats.get(message.chat.id)
    if not cur:
        return await message.reply_text("❌ Nothing is playing.")
    await message.reply_text(
        now_playing(cur, paused=message.chat.id in paused),
        reply_markup=player(paused=message.chat.id in paused),
        disable_web_page_preview=True,
    )


@Client.on_message(filters.command(["qclear", "clearqueue"], PREFIXES) & filters.group)
async def qclear_cmd(client, message: Message):
    queues[message.chat.id] = []
    await message.reply_text("🧹 **Queue cleared.**")


@Client.on_message(filters.command("qjump", PREFIXES) & filters.group)
@require_assistant
async def qjump_cmd(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: `/qjump <number>`")
    try:
        idx = int(message.command[1]) - 1
    except ValueError:
        return await message.reply_text("❌ Number daalo.")
    chat_id = message.chat.id
    q = queues.get(chat_id, [])
    if not q or idx < 0 or idx >= len(q):
        return await message.reply_text("❌ Invalid index.")
    # move selected track to top of queue
    track = q.pop(idx)
    q.insert(0, track)
    await message.reply_text(f"⏭ **Moved to top:** `{track['title'][:40]}`")


@Client.on_message(filters.command("shuffle", PREFIXES) & filters.group)
async def shuffle_cmd(client, message: Message):
    import random
    chat_id = message.chat.id
    q = queues.get(chat_id, [])
    if not q:
        return await message.reply_text("📭 Queue is empty.")
    random.shuffle(q)
    queues[chat_id] = q
    await message.reply_text(f"🔀 **Shuffled {len(q)} tracks.**")


@Client.on_message(filters.command("loop", PREFIXES) & filters.group)
async def loop_cmd(client, message: Message):
    chat_id = message.chat.id
    if len(message.command) < 2:
        cur = await get(chat_id, "loop", "off")
        return await message.reply_text(
            f"🔁 **Loop mode:** `{cur}`\n\n"
            "Usage: `/loop off|song|queue`"
        )
    mode = message.command[1].lower()
    if mode not in ("off", "song", "queue"):
        return await message.reply_text("❌ Modes: `off`, `song`, `queue`")
    await set_setting(chat_id, "loop", mode)
    await message.reply_text(f"🔁 **Loop set to:** `{mode}`")
