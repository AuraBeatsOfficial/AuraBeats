"""AuraBeats - FFmpeg preset builders."""

# Base chain - always applied
_BASE = "aresample=48000,aformat=sample_fmts=s16:channel_layouts=stereo"

PRESETS = {
    # name -> filter chain
    "flat":      _BASE,
    "bass":      f"{_BASE},equalizer=f=100:width_type=h:width=200:g=10,"
                 f"equalizer=f=200:width_type=h:width=200:g=6",
    "treble":    f"{_BASE},equalizer=f=8000:width_type=h:width=2000:g=8,"
                 f"equalizer=f=12000:width_type=h:width=2000:g=6",
    "vocal":     f"{_BASE},equalizer=f=3000:width_type=h:width=1500:g=8,"
                 f"equalizer=f=1000:width_type=h:width=800:g=4",
    "nightcore": f"{_BASE},asetrate=48000*1.25,aresample=48000,atempo=1.05",
    "slowed":    f"{_BASE},asetrate=48000*0.85,aresample=48000,atempo=1.0",
    "lofi":      f"{_BASE},lowpass=f=3500,highpass=f=120,volume=0.85",
    "8d":        f"{_BASE},apulsator=hz=0.08:mode=vinyl",
    "3d":        f"{_BASE},apulsator=hz=0.12:mode=square",
    "acoustic":  f"{_BASE},highpass=f=80,lowpass=f=12000,"
                 f"equalizer=f=250:width_type=h:width=200:g=4",
    "clear":     f"{_BASE},highpass=f=60,lowpass=f=16000,"
                 f"equalizer=f=2500:width_type=h:width=1000:g=3",
    "echo":      f"{_BASE},aecho=0.8:0.88:60:0.4",
    "reverb":    f"{_BASE},aecho=0.8:0.9:40|60:0.4|0.3",
}


def get_filter(preset: str) -> str | None:
    """Return ffmpeg audio filter string for preset (None = no filter)."""
    if not preset:
        return None
    return PRESETS.get(preset.lower())


def list_presets() -> list:
    return sorted(PRESETS.keys())


def pitch_shift(semitones: int) -> str:
    """Pitch shift filter (semitone -12..+12)."""
    rate = 48000 * (2 ** (semitones / 12))
    return f"{_BASE},asetrate={int(rate)},aresample=48000,atempo={48000/rate:.4f}"


def speed_change(factor: float) -> str:
    """Speed change (0.5x..2.0x)."""
    factor = max(0.5, min(2.0, factor))
    return f"{_BASE},atempo={factor:.3f}"


def volume_boost(percent: int) -> str:
    """Volume 1..200%."""
    percent = max(1, min(200, percent))
    gain = (percent - 100) / 100 * 20  # dB
    return f"{_BASE},volume={gain:+.1f}dB"
