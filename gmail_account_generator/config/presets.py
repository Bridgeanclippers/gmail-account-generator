"""Fingerprint presets. Kept small — the real pool lives in adapters."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FingerprintPreset:
    name: str
    chrome_major: int
    platform: str
    webgl_vendor: str
    timezone: str
    languages: tuple[str, ...]


_PRESETS: dict[str, FingerprintPreset] = {
    "chrome_win_2026": FingerprintPreset(
        name="chrome_win_2026",
        chrome_major=134,
        platform="Win32",
        webgl_vendor="Google Inc. (NVIDIA)",
        timezone="America/New_York",
        languages=("en-US", "en"),
    ),
    "chrome_win_2025": FingerprintPreset(
        name="chrome_win_2025",
        chrome_major=126,
        platform="Win32",
        webgl_vendor="Google Inc. (Intel)",
        timezone="Europe/Berlin",
        languages=("en-GB", "en"),
    ),
}


def load_preset(name: str) -> FingerprintPreset:
    if name not in _PRESETS:
        raise KeyError(f"unknown fingerprint preset: {name}")
    return _PRESETS[name]