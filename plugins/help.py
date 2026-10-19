"""AuraBeats - /help command menu."""
from pyrogram import Client, filters
from pyrogram.types import Message

from config import PREFIXES, BOT_NAME

HELP_TEXT = f"""
**🎼 {BOT_NAME} — Command Menu**

**▶️ Playback**
`/play <song|url>` — audio
`/vplay <song|url>` — video
`/pause` `/resume` `/skip` `/stop`

**🎚 Controls**
`/seek <1:30>` — jump
`/volume <1-200>`

**🎧 Queue**
`/queue` — show queue
`/nowplaying` — current track
`/qclear` — clear queue

**🎛 Effects**
`/eq <preset>` — bass · nightcore · 8d · lofi ·
slowed · vocal · acoustic · clear · 3d · treble

**📥 Downloads**
`/song <name>` — audio file
`/video <name>` — video file

**🎼 Playlists**
`/pl create|add|view|del|load <name>`

**🧠 AI**
`/aimood <mood>` · `/lyrics <song>`

**🛡 Admin**
`/settings` · `/stats` · `/broadcast`

**ℹ️ Info**
`/ping` · `/help`
"""


@Client.on_message(filters.command("help", PREFIXES))
async def help_cmd(client, message: Message):
    await message.reply_text(HELP_TEXT)


@Client.on_message(filters.command("ping", PREFIXES))
async def ping_cmd(client, message: Message):
    import time
    t = time.time()
    m = await message.reply_text("🏓 Pong…")
    await m.edit_text(f"🏓 **Pong!** `{(time.time()-t)*1000:.1f} ms`")
