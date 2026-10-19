"""AuraBeats - /vplay handler (video streaming)."""
from pyrogram import Client, filters
from pyrogram.types import Message

from config import PREFIXES
from utils.decorators import require_assistant
from plugins.play import _handle_play


@Client.on_message(filters.command("vplay", PREFIXES) & filters.group)
@require_assistant
async def vplay_cmd(client, message: Message):
    await _handle_play(client, message, is_video=True)
