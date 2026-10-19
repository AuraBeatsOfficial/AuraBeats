"""AuraBeats - Admin commands (/broadcast /ban /unban /maintenance)."""
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message

from config import PREFIXES, OWNER_ID, SUDO_USERS
from core.database import db
from database.users import (
    ban_user, unban_user, is_banned, count_users,
)
from database.chats import get_all_chat_ids, count_chats
from utils.decorators import require_sudo
from utils.logger import get_logger

log = get_logger("AuraBeats.Admin")


@Client.on_message(filters.command("broadcast", PREFIXES) & filters.private)
@require_sudo
async def broadcast_cmd(client, message: Message):
    """Broadcast to all chats (or replied message to broadcast that)."""
    target_msg = message.reply_to_message or message
    text = target_msg.text or target_msg.caption
    if not text:
        return await message.reply_text("❌ Reply to a message or include text.")

    chat_ids = await get_all_chat_ids()
    if not chat_ids:
        return await message.reply_text("📭 No known chats to broadcast to.")

    status = await message.reply_text(
        f"📢 **Broadcasting to {len(chat_ids)} chats…**"
    )

    sent, failed = 0, 0
    for cid in chat_ids:
        try:
            await client.send_message(cid, text)
            sent += 1
        except Exception:
            failed += 1
        await asyncio.sleep(0.1)  # flood safety

    await status.edit_text(
        f"📢 **Broadcast done**\n\n"
        f"✅ Sent: `{sent}`\n"
        f"❌ Failed: `{failed}`"
    )


@Client.on_message(filters.command("ban", PREFIXES) & filters.private)
@require_sudo
async def ban_cmd(client, message: Message):
    target = None
    if message.reply_to_message and message.reply_to_message.from_user:
        target = message.reply_to_message.from_user.id
    elif len(message.command) > 1:
        try:
            target = int(message.command[1])
        except ValueError:
            return await message.reply_text("Usage: `/ban <user_id>` or reply to user.")
    if not target:
        return await message.reply_text("❌ No user specified.")
    if target in SUDO_USERS or target == OWNER_ID:
        return await message.reply_text("❌ Can't ban sudo/owner.")
    await ban_user(target)
    await message.reply_text(f"🚫 **Banned:** `{target}`")


@Client.on_message(filters.command("unban", PREFIXES) & filters.private)
@require_sudo
async def unban_cmd(client, message: Message):
    target = None
    if message.reply_to_message and message.reply_to_message.from_user:
        target = message.reply_to_message.from_user.id
    elif len(message.command) > 1:
        try:
            target = int(message.command[1])
        except ValueError:
            return await message.reply_text("Usage: `/unban <user_id>`")
    if not target:
        return await message.reply_text("❌ No user specified.")
    await unban_user(target)
    await message.reply_text(f"✅ **Unbanned:** `{target}`")


@Client.on_message(filters.command("maintenance", PREFIXES) & filters.private)
@require_sudo
async def maintenance_cmd(client, message: Message):
    """Toggle maintenance mode (stored in DB settings for chat 0)."""
    from core.settings import get, set as set_setting
    cur = await get(0, "maintenance", False)
    new = not cur
    await set_setting(0, "maintenance", new)
    state = "🔴 ON" if new else "🟢 OFF"
    await message.reply_text(f"🛠 **Maintenance mode:** {state}")


@Client.on_message(filters.command("blacklist", PREFIXES) & filters.private)
@require_sudo
async def blacklist_cmd(client, message: Message):
    """List blacklisted users."""
    if not db.online:
        return await message.reply_text("⚠️ DB offline.")
    try:
        users = []
        async for doc in db.users.find({"banned": True}, {"user_id": 1}):
            users.append(doc["user_id"])
        if not users:
            return await message.reply_text("📭 No banned users.")
        lines = ["**🚫 Blacklisted Users**", ""]
        for u in users[:50]:
            lines.append(f"`{u}`")
        await message.reply_text("\n".join(lines))
    except Exception as e:
        await message.reply_text(f"❌ `{e}`")
