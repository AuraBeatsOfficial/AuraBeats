"""AuraBeats - /pl personal playlists."""
from pyrogram import Client, filters
from pyrogram.types import Message

from config import PREFIXES, FEATURE_PLAYLIST
from database.playlists import (
    create_playlist, add_track, get_playlist,
    list_playlists, delete_playlist, remove_track,
)
from utils.formatters import humanize_duration, truncate


def _uid(m): return m.from_user.id if m.from_user else 0


@Client.on_message(filters.command("pl", PREFIXES) & filters.private)
async def pl_cmd(client, message: Message):
    if not FEATURE_PLAYLIST:
        return await message.reply_text("⚠️ Playlists disabled.")

    args = message.command[1:]
    if not args:
        return await message.reply_text(
            "**🎼 Playlist Commands**\n\n"
            "`/pl create <name>`\n"
            "`/pl list`\n"
            "`/pl view <name>`\n"
            "`/pl add <name>` — reply to a /play or with URL\n"
            "`/pl del <name>`\n"
            "`/pl rm <name> <index>`"
        )

    action = args[0].lower()
    uid = _uid(message)

    if action == "create":
        if len(args) < 2:
            return await message.reply_text("Usage: `/pl create <name>`")
        name = " ".join(args[1:])
        await create_playlist(uid, name)
        return await message.reply_text(f"✅ Playlist created: `{name}`")

    if action == "list":
        names = await list_playlists(uid)
        if not names:
            return await message.reply_text("📭 No playlists yet.")
        lines = ["**🎼 Your Playlists**", ""]
        for i, n in enumerate(names, 1):
            lines.append(f"`{i}.` {n}")
        return await message.reply_text("\n".join(lines))

    if action == "view":
        if len(args) < 2:
            return await message.reply_text("Usage: `/pl view <name>`")
        name = " ".join(args[1:])
        tracks = await get_playlist(uid, name)
        if not tracks:
            return await message.reply_text(f"📭 Playlist `{name}` is empty.")
        lines = [f"**🎼 {name}** ({len(tracks)} tracks)", ""]
        for i, t in enumerate(tracks[:20], 1):
            lines.append(f"`{i}.` {truncate(t.get('title','?'), 40)} "
                         f"`{humanize_duration(t.get('duration', 0))}`")
        if len(tracks) > 20:
            lines.append(f"_…and {len(tracks)-20} more_")
        return await message.reply_text("\n".join(lines))

    if action == "add":
        if len(args) < 2:
            return await message.reply_text("Usage: `/pl add <name>` (reply to song or include query)")
        name = args[1]
        query = " ".join(args[2:]) if len(args) > 2 else ""
        if not query and message.reply_to_message:
            query = message.reply_to_message.text or ""
        if not query:
            return await message.reply_text("❌ Provide a song name or URL.")
        from utils.yt_helper import search
        try:
            info = await search(query)
        except Exception as e:
            return await message.reply_text(f"❌ Search failed: `{e}`")
        track = {
            "title":    info["title"],
            "url":      info["url"],
            "webpage":  info.get("webpage"),
            "duration": info.get("duration", 0),
        }
        await add_track(uid, name, track)
        return await message.reply_text(
            f"✅ Added to `{name}`:\n**{track['title'][:60]}**"
        )

    if action == "del":
        if len(args) < 2:
            return await message.reply_text("Usage: `/pl del <name>`")
        name = " ".join(args[1:])
        await delete_playlist(uid, name)
        return await message.reply_text(f"🗑 Deleted: `{name}`")

    if action == "rm":
        if len(args) < 3:
            return await message.reply_text("Usage: `/pl rm <name> <index>`")
        name = args[1]
        try:
            idx = int(args[2]) - 1
        except ValueError:
            return await message.reply_text("❌ Index must be a number.")
        await remove_track(uid, name, idx)
        return await message.reply_text(f"🗑 Removed from `{name}`.")

    return await message.reply_text("❌ Unknown action. Try `/pl` for help.")
