"""AuraBeats - Inline search (@AuraBeatsOfficialBot <query>)."""
from pyrogram import Client
from pyrogram.types import (
    InlineQuery, InlineQueryResultArticle, InputTextMessageContent,
    InlineKeyboardMarkup, InlineKeyboardButton,
)

from config import FEATURE_INLINE, BOT_USERNAME
from utils.yt_helper import search
from utils.formatters import humanize_duration, compact_number, truncate
from utils.logger import get_logger

log = get_logger("AuraBeats.Inline")


@Client.on_inline_query()
async def inline_handler(client, query: InlineQuery):
    if not FEATURE_INLINE:
        return await query.answer([], cache_time=10)

    text = query.query.strip()
    if not text:
        results = [
            InlineQueryResultArticle(
                title="🎵 AuraBeats — Inline Search",
                description="Type a song name to search",
                input_message_content=InputTextMessageContent(
                    f"🎵 Use @{BOT_USERNAME} inline!\n"
                    f"Type any song name in any chat."
                ),
            ),
            InlineQueryResultArticle(
                title="📖 Help",
                description="View all commands",
                input_message_content=InputTextMessageContent(
                    f"📖 Send /help to @{BOT_USERNAME} for commands"
                ),
            ),
        ]
        return await query.answer(results, cache_time=30, is_personal=True)

    try:
        info = await search(text)
    except Exception as e:
        log.warning(f"inline search failed: {e}")
        return await query.answer(
            [InlineQueryResultArticle(
                title="❌ Search failed",
                description=str(e)[:100],
                input_message_content=InputTextMessageContent(
                    f"❌ Couldn't find: {text}"
                ),
            )],
            cache_time=5,
        )

    title = info["title"]
    dur = humanize_duration(info.get("duration", 0))
    uploader = info.get("uploader", "—")
    views = compact_number(info.get("views", 0))

    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("▶️ Play in group", url=f"https://t.me/{BOT_USERNAME}?startgroup=true"),
        InlineKeyboardButton("🔗 YouTube", url=info.get("webpage", "https://youtube.com")),
    ]])

    play_cmd = f"/play {info.get('webpage') or text}"
    results = [
        InlineQueryResultArticle(
            title=truncate(title, 60),
            description=f"{dur} · {uploader} · {views} views",
            thumb_url=info.get("thumbnail") if False else None,
            input_message_content=InputTextMessageContent(
                f"🎵 **{truncate(title, 60)}**\n"
                f"⏱ `{dur}`\n"
                f"🎙 {uploader}\n\n"
                f"Send `{play_cmd}` in a group to play."
            ),
            reply_markup=kb,
        ),
    ]
    await query.answer(results, cache_time=15, is_personal=True)
