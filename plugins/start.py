"""AuraBeats - /start welcome card."""
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from config import PREFIXES, BOT_NAME, BOT_USERNAME
from utils.keyboard import start_menu
from utils.logger import get_logger

log = get_logger("AuraBeats.Start")

START_TEXT = f"""
🎵 **Welcome to {BOT_NAME}**

India's most advanced **AI music bot** for Telegram voice chats.

**✨ Highlights**
• 🚀 Zero-latency streaming engine
• 🎚 Live DSP effects (bass · nightcore · 8d · lofi)
• 🧠 AI mood playlists
• 📥 Multi-platform downloader
• 🎤 Synced lyrics

**📌 Quick Start**
1. Add me to a group
2. Add my assistant
3. Start a voice chat
4. Send `/play <song name>`

Tap **/help** for all commands.
"""


@Client.on_message(filters.command("start", PREFIXES) & filters.private)
async def start_private(client, message: Message):
    await message.reply_text(
        START_TEXT,
        reply_markup=start_menu(BOT_USERNAME),
        disable_web_page_preview=True,
    )


@Client.on_message(filters.command("start", PREFIXES) & filters.group)
async def start_group(client, message: Message):
    await message.reply_text(
        f"👋 **{BOT_NAME} is online!**\n\n"
        f"Use `/play <song>` to start streaming in voice chat.",
    )
