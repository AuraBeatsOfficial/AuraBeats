"""
AuraBeats - Central Logger
Colored console + optional file logging.
Usage:
    from utils.logger import get_logger
    log = get_logger(__name__)
    log.info("hello")
"""
import logging
import sys
from pathlib import Path

# ---------- ANSI colors ----------
class _Colors:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    GREY    = "\033[90m"
    RED     = "\033[91m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    BLUE    = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN    = "\033[96m"
    WHITE   = "\033[97m"


_LEVEL_COLORS = {
    logging.DEBUG:    _Colors.GREY,
    logging.INFO:     _Colors.CYAN,
    logging.WARNING:  _Colors.YELLOW,
    logging.ERROR:    _Colors.RED,
    logging.CRITICAL: _Colors.MAGENTA,
}


class ColorFormatter(logging.Formatter):
    """Colored console formatter."""

    def format(self, record: logging.LogRecord) -> str:
        color = _LEVEL_COLORS.get(record.levelno, _Colors.WHITE)
        lvl   = f"{color}{_Colors.BOLD}{record.levelname:<8}{_Colors.RESET}"
        name  = f"{_Colors.BLUE}{record.name}{_Colors.RESET}"
        time  = f"{_Colors.GREY}{self.formatTime(record, '%H:%M:%S')}{_Colors.RESET}"
        msg   = record.getMessage()
        base  = f"{time} {lvl} {name} » {msg}"

        if record.exc_info:
            base += "\n" + self.formatException(record.exc_info)
        return base


# ---------- state ----------
_initialized = False
_LOG_DIR = Path("logs")
_LOG_FILE = _LOG_DIR / "aurabeats.log"

# Libraries to silence (only warnings+)
_SILENT = (
    "pyrogram", "pytgcalls", "pyrogram.session", "pyrogram.connection",
    "pyrogram.methods", "pyrogram.crypto",
    "httpx", "httpcore", "aiohttp",
    "motor", "pymongo",
    "yt_dlp", "urllib3",
)


def setup(level: int = logging.INFO, file_log: bool = True) -> None:
    """Initialize root logger once."""
    global _initialized
    if _initialized:
        return

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()

    # Console handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(ColorFormatter())
    ch.setLevel(level)
    root.addHandler(ch)

    # File handler (rotate-friendly, plain text)
    if file_log:
        try:
            _LOG_DIR.mkdir(exist_ok=True)
            fh = logging.FileHandler(_LOG_FILE, encoding="utf-8")
            fh.setFormatter(logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
            ))
            fh.setLevel(level)
            root.addHandler(fh)
        except Exception:
            pass

    # Silence noisy libraries
    for noisy in _SILENT:
        logging.getLogger(noisy).setLevel(logging.WARNING)

    _initialized = True


def get_logger(name: str) -> logging.Logger:
    """Get a named logger (auto-initializes root on first call)."""
    if not _initialized:
        setup()
    return logging.getLogger(name)


# ---------- self-test ----------
if __name__ == "__main__":
    setup()
    log = get_logger("AuraBeats.Test")
    log.debug("this is debug")
    log.info("this is info")
    log.warning("this is warning")
    log.error("this is error")
    log.critical("this is critical")
    try:
        1 / 0
    except ZeroDivisionError:
        log.exception("caught exception demo")
    print("\ncheck logs/aurabeats.log for file output")
