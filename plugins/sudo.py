"""AuraBeats - Sudo commands (/restart /logs /sys)."""
import os
import sys
import time
import platform
import psutil
from pyrogram import Client, filters
from pyrogram.types import Message

from config import PREFIXES
from utils.decorators import require_sudo
from utils.formatters import humanize_bytes, humanize_duration

_START = time.time()


@Client.on_message(filters.command("restart", PREFIXES) & filters.private)
@require_sudo
async def restart_cmd(client, message: Message):
    await message.reply_text("♻️ **Restarting…**")
    os.execv(sys.executable, [sys.executable, "AuraBeats"])


@Client.on_message(filters.command("logs", PREFIXES) & filters.private)
@require_sudo
async def logs_cmd(client, message: Message):
    path = "logs/aurabeats.log"
    if not os.path.exists(path):
        return await message.reply_text("❌ No log file yet.")
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()[-100:]
        text = "".join(lines)[-3800:]
        await message.reply_text(f"📜 **Last 100 log lines**\n\n```\n{text}\n```")
    except Exception as e:
        await message.reply_text(f"❌ `{e}`")


@Client.on_message(filters.command("sys", PREFIXES) & filters.private)
@require_sudo
async def sys_cmd(client, message: Message):
    try:
        uptime = int(time.time() - _START)
        vm = psutil.virtual_memory()
        disk = psutil.disk_usage(".")
        cpu = psutil.cpu_percent(interval=0.5)

        text = (
            f"**🖥 System Info**\n\n"
            f"**OS:** `{platform.system()} {platform.release()}`\n"
            f"**Python:** `{platform.python_version()}`\n"
            f"**Uptime:** `{humanize_duration(uptime)}`\n\n"
            f"**CPU:** `{cpu}%`\n"
            f"**RAM:** `{humanize_bytes(vm.used)}/{humanize_bytes(vm.total)}` "
            f"(`{vm.percent}%`)\n"
            f"**Disk:** `{humanize_bytes(disk.used)}/{humanize_bytes(disk.total)}` "
            f"(`{disk.percent}%`)\n"
        )
        await message.reply_text(text)
    except ImportError:
        await message.reply_text("⚠️ `psutil` not installed. `pip install psutil`")
    except Exception as e:
        await message.reply_text(f"❌ `{e}`")


@Client.on_message(filters.command("dbbackup", PREFIXES) & filters.private)
@require_sudo
async def dbbackup_cmd(client, message: Message):
    """Simple DB export to JSON file."""
    from core.database import db
    if not db.online:
        return await message.reply_text("⚠️ DB offline — nothing to backup.")
    try:
        import json
        from datetime import datetime
        out = {}
        for coll in ("users", "chats", "playlists", "settings", "stats"):
            docs = []
            async for d in db[coll].find({}):
                d.pop("_id", None)
                docs.append(d)
            out[coll] = docs
        fname = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(fname, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=2, default=str)
        size = humanize_bytes(os.path.getsize(fname))
        await message.reply_document(fname, caption=f"🗄 DB Backup · {size}")
        os.remove(fname)
    except Exception as e:
        await message.reply_text(f"❌ `{e}`")
