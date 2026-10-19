"""
AuraBeats - Assistant Userbot
Joins group voice chats to stream audio.
"""
from pyrogram import Client
from config import API_ID, API_HASH, SESSION, ASSISTANT_USERNAME
from utils.logger import get_logger

log = get_logger("AuraBeats.Assistant")

assistant = None

if SESSION:
    assistant = Client(
        name="AuraBeatsAssistant",
        api_id=API_ID,
        api_hash=API_HASH,
        session_string=SESSION,
        in_memory=True,
    )
    log.info(f"Assistant client prepared: @{ASSISTANT_USERNAME}")
else:
    log.warning("SESSION not set — voice chat features disabled")


async def start_assistant():
    if not assistant:
        return None
    log.info("Starting assistant...")
    await assistant.start()
    me = await assistant.get_me()
    log.info(f"Assistant online: @{me.username} (id={me.id})")
    return me


async def stop_assistant():
    if not assistant:
        return
    log.info("Stopping assistant...")
    try:
        await assistant.stop()
    except Exception as e:
        log.warning(f"assistant stop failed: {e}")
