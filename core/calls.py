"""
AuraBeats - PyTgCalls Stream Engine
Manages voice chat streaming, runtime queue state.
"""
from config import MAX_QUEUE_SIZE
from utils.logger import get_logger

log = get_logger("AuraBeats.Calls")

call_py = None

try:
    from pytgcalls import PyTgCalls
    from core.userbot import assistant
    if assistant is not None:
        call_py = PyTgCalls(assistant)
        log.info("PyTgCalls engine prepared")
    else:
        log.warning("No assistant — call engine disabled")
except ImportError as e:
    log.warning(f"pytgcalls not installed: {e}")
except Exception as e:
    log.warning(f"call engine init failed: {e}")


queues: dict = {}
active_chats: dict = {}
paused: set = set()


def is_active(chat_id: int) -> bool:
    return chat_id in active_chats


def get_queue(chat_id: int) -> list:
    return queues.setdefault(chat_id, [])


def queue_size(chat_id: int) -> int:
    return len(queues.get(chat_id, []))


def push_track(chat_id: int, track: dict) -> bool:
    q = get_queue(chat_id)
    if len(q) >= MAX_QUEUE_SIZE:
        return False
    q.append(track)
    return True


def pop_next(chat_id: int):
    q = queues.get(chat_id, [])
    return q.pop(0) if q else None


def clear_chat(chat_id: int):
    queues.pop(chat_id, None)
    active_chats.pop(chat_id, None)
    paused.discard(chat_id)


async def start_engine():
    if not call_py:
        return False
    try:
        await call_py.start()
        log.info("PyTgCalls engine online")
        return True
    except Exception as e:
        log.error(f"call engine start failed: {e}")
        return False


async def stop_engine():
    if not call_py:
        return
    try:
        await call_py.stop()
        log.info("PyTgCalls engine stopped")
    except Exception as e:
        log.warning(f"call engine stop failed: {e}")
