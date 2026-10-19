"""AuraBeats - Custom exceptions."""


class AuraError(Exception):
    """Base."""


class NoAssistant(AuraError):
    """Assistant not configured / not in VC."""


class NotInVC(AuraError):
    """Bot not in voice chat."""


class NoActiveStream(AuraError):
    """Nothing currently playing."""


class QueueFull(AuraError):
    """Queue reached max size."""


class SearchFailed(AuraError):
    """yt-dlp / search failed."""


class DownloadFailed(AuraError):
    """Download failed."""


class FFmpegError(AuraError):
    """FFmpeg processing failed."""


class InvalidInput(AuraError):
    """Bad user input."""


class AdminRequired(AuraError):
    """Admin permission required."""


class SudoRequired(AuraError):
    """Sudo permission required."""


class RateLimited(AuraError):
    """User hit rate limit."""
