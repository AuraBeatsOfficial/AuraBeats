"""AuraBeats - Central callback dispatcher (all cb:* buttons)."""
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery

from core.calls import call_py, active_chats, queues, paused, pop_next, clear_chat
from utils.keyboard import player, eq_menu, queue_page, start_menu
from utils.inline_ui import now_playing, queue_card
from utils.streamer import build_audio
from utils.ffmpeg import list_presets
from utils.logger import get_logger

log = get_logger("AuraBeats.Callback")


async def _safe_pause(chat_id):
    if hasattr(call_py, "pause_stream"):
        await call_py.pause_stream(chat_id)
    else:
        await call_py.pause(chat_id)


async def _safe_resume(chat_id):
    if hasattr(call_py, "resume_stream"):
        await call_py.resume_stream(chat_id)
    else:
        await call_py.resume(chat_id)


async def _next_track(chat_id):
    nxt = pop_next(chat_id)
    if not nxt:
        try:
            await call_py.leave_call(chat_id)
        except Exception:
            pass
        active_chats.pop(chat_id, None)
        paused.discard(chat_id)
        return None
    try:
        await call_py.play(chat_id, build_audio(nxt["url"]))
        active_chats[chat_id] = nxt
        paused.discard(chat_id)
        return nxt
    except Exception as e:
        log.warning(f"next_track failed: {e}")
        return None


@Client.on_callback_query(filters.regex(r"^cb:"))
async def cb_router(client, q: CallbackQuery):
    data = q.data
    chat_id = q.message.chat.id

    # ---------- player actions ----------
    if data == "cb:pause":
        if chat_id not in active_chats:
            return await q.answer("Nothing playing", show_alert=True)
        try:
            await _safe_pause(chat_id)
            paused.add(chat_id)
            await q.message.edit_reply_markup(player(paused=True))
            await q.answer("Paused")
        except Exception as e:
            await q.answer(f"Error: {e}", show_alert=True)

    elif data == "cb:resume":
        if chat_id not in active_chats:
            return await q.answer("Nothing playing", show_alert=True)
        try:
            await _safe_resume(chat_id)
            paused.discard(chat_id)
            await q.message.edit_reply_markup(player(paused=False))
            await q.answer("Resumed")
        except Exception as e:
            await q.answer(f"Error: {e}", show_alert=True)

    elif data == "cb:skip":
        if chat_id not in active_chats:
            return await q.answer("Nothing playing", show_alert=True)
        nxt = await _next_track(chat_id)
        if nxt:
            await q.message.edit_text(
                now_playing(nxt),
                reply_markup=player(paused=False),
                disable_web_page_preview=True,
            )
            await q.answer(f"Skipped → {nxt['title'][:30]}")
        else:
            await q.answer("Queue empty — stopped")
            try:
                await q.message.delete()
            except Exception:
                pass

    elif data == "cb:stop":
        try:
            await call_py.leave_call(chat_id)
        except Exception:
            pass
        clear_chat(chat_id)
        await q.answer("Stopped")
        try:
            await q.message.delete()
        except Exception:
            pass

    # ---------- queue view ----------
    elif data == "cb:queue":
        q_list = queues.get(chat_id, [])
        cur = active_chats.get(chat_id)
        await q.message.edit_text(
            queue_card(q_list, cur),
            reply_markup=queue_page(q_list, 0),
        )
        await q.answer()

    elif data.startswith("cb:qpage:"):
        try:
            page = int(data.split(":")[-1])
        except ValueError:
            return await q.answer("Invalid")
        q_list = queues.get(chat_id, [])
        await q.message.edit_reply_markup(queue_page(q_list, page))
        await q.answer()

    # ---------- effects ----------
    elif data == "cb:eq_menu":
        if chat_id not in active_chats:
            return await q.answer("Start a song first", show_alert=True)
        await q.message.edit_text(
            "🎚 **Choose an effect**\n\n"
            "_Effects apply to the next track if queue is active._",
            reply_markup=eq_menu(),
        )
        await q.answer()

    elif data.startswith("cb:eq:"):
        preset = data.split(":", 2)[-1]
        if preset not in list_presets():
            return await q.answer("Unknown preset", show_alert=True)
        cur = active_chats.get(chat_id)
        if not cur:
            return await q.answer("Nothing playing", show_alert=True)
        # re-stream with effect
        try:
            await call_py.play(chat_id, build_audio(cur["url"], preset=preset))
            await q.answer(f"Applied: {preset}")
            await q.message.edit_reply_markup(player(paused=False))
        except Exception as e:
            await q.answer(f"Failed: {e}", show_alert=True)

    elif data == "cb:back_player":
        cur = active_chats.get(chat_id)
        if cur:
            await q.message.edit_text(
                now_playing(cur),
                reply_markup=player(paused=chat_id in paused),
                disable_web_page_preview=True,
            )
        await q.answer()

    # ---------- shuffle / loop ----------
    elif data == "cb:shuffle":
        import random
        q_list = queues.get(chat_id, [])
        if not q_list:
            return await q.answer("Queue empty", show_alert=True)
        random.shuffle(q_list)
        queues[chat_id] = q_list
        await q.answer("🔀 Shuffled")

    elif data == "cb:loop":
        from core.settings import get, set
        cur = await get(chat_id, "loop", "off")
        nxt = {"off": "song", "song": "queue", "queue": "off"}.get(cur, "off")
        await set(chat_id, "loop", nxt)
        await q.answer(f"🔁 Loop: {nxt}")

    # ---------- nav / utility ----------
    elif data == "cb:help":
        from plugins.help import HELP_TEXT
        await q.message.edit_text(HELP_TEXT)
        await q.answer()

    elif data == "cb:close":
        try:
            await q.message.delete()
        except Exception:
            pass
        await q.answer()

    elif data == "cb:noop":
        await q.answer()

    else:
        await q.answer("Unknown action")
