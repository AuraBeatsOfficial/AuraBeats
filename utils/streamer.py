"""AuraBeats - MediaStream builder (zero-file, direct URL)."""
from pytgcalls.types import MediaStream, AudioQuality, VideoQuality

from utils.ffmpeg import get_filter
from utils.logger import get_logger

log = get_logger("AuraBeats.Streamer")


def build_audio(url: str, preset: str | None = None) -> MediaStream:
    """Build an audio MediaStream, optionally with DSP preset."""
    try:
        if preset:
            f = get_filter(preset)
            if f:
                return MediaStream(
                    url,
                    audio_parameters=AudioQuality.HIGH,
                    ffmpeg_parameters=f"-af \"{f}\"",
                )
        return MediaStream(url, audio_parameters=AudioQuality.HIGH)
    except Exception as e:
        log.warning(f"build_audio failed: {e}")
        raise


def build_video(url: str) -> MediaStream:
    """Build a video MediaStream."""
    try:
        return MediaStream(
            url,
            audio_parameters=AudioQuality.HIGH,
            video_parameters=VideoQuality.HD_720p,
        )
    except Exception as e:
        log.warning(f"build_video failed: {e}")
        raise


def build_raw(url: str) -> MediaStream:
    """Minimal stream - just audio."""
    return MediaStream(url, audio_parameters=AudioQuality.MEDIUM)
