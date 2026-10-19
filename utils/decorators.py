"""AuraBeats - Command decorators."""
from functools import wraps
from pyrogram.enums import ChatMemberStatus

from config import OWNER_ID, SUDO_USERS
from core.calls import call_py
from utils.logger import get_logger

log = get_logger("AuraBeats.Decorators")

_ADMIN_STATES = (
    ChatMemberStatus.OWNER,
    ChatMemberStatus.ADMINISTRATOR,
)


def require_assistant(func):
    """Block command if assistant/PyTgCalls not configured."""
    @wraps(func)
    async def wrapper(client, message, *a, **kw):
        if not call_py:
            return await message.reply_text(
                "⚠️ **Assistant not configured.**\n"
                "Voice chat features need a `SESSION` in `.env`."
            )
        return await func(client, message, *a, **kw)
    return wrapper


def require_admin(func):
    """Only chat admins (or sudo) can use."""
    @wraps(func)
    async def wrapper(client, message, *a, **kw):
        uid = message.from_user.id if message.from_user else 0
        if uid == OWNER_ID or uid in SUDO_USERS:
            return await func(client, message, *a, **kw)
        try:
            member = await client.get_chat_member(message.chat.id, uid)
            if member.status in _ADMIN_STATES:
                return await func(client, message, *a, **kw)
        except Exception:
            pass
        return await message.reply_text("🛡️ **Admin only.**")
    return wrapper


def require_sudo(func):
    """Only owner / sudo users."""
    @wraps(func)
    async def wrapper(client, message, *a, **kw):
        uid = message.from_user.id if message.from_user else 0
        if uid == OWNER_ID or uid in SUDO_USERS:
            return await func(client, message, *a, **kw)
        return await message.reply_text("🛡️ **Sudo only.**")
    return wrapper


def rate_limit(seconds: int = 3):
    """Simple per-user cooldown."""
    def decorator(func):
        last = {}
        @wraps(func)
        async def wrapper(client, message, *a, **kw):
            import time
            uid = message.from_user.id if message.from_user else 0
            now = time.time()
            if uid in last and now - last[uid] < seconds:
                wait = int(seconds - (now - last[uid]))
                try:
                    await message.reply_text(f"⏳ Wait `{wait}s` before next command.")
                except Exception:
                    pass
                return
            last[uid] = now
            return await func(client, message, *a, **kw)
        return wrapper
    return decorator
