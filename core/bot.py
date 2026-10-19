"""
AuraBeats - Bot Client (Pyrogram)
Auto-loads plugins/ folder, no manual imports.
"""
from pyrogram import Client
from pyrogram.enums import ParseMode

from config import API_ID, API_HASH, BOT_TOKEN, BOT_NAME, PREFIXES
from utils.logger import get_logger

log = get_logger("AuraBeats.Bot")


class AuraBot(Client):
    """Bot client wrapper."""

    def __init__(self):
        super().__init__(
            name="AuraBeats",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            plugins=dict(root="plugins"),
            in_memory=True,
            parse_mode=ParseMode.MARKDOWN,
            sleep_threshold=15,
            workers=16,
        )

    async def start_bot(self):
        log.info(f"Starting bot ({BOT_NAME})...")
        await self.start()
        me = await self.get_me()
        log.info(f"Bot online: @{me.username} (id={me.id})")
        return me

    async def stop_bot(self):
        log.info("Stopping bot...")
        try:
            await self.stop()
        except Exception as e:
            log.warning(f"stop failed: {e}")


bot = AuraBot()
