"""Persistent settings, stored as JSON next to the tool."""

from __future__ import annotations

import json
import os

from . import paths
from .keys import DEFAULT_KEY_LABEL

DEFAULTS = {
    "console_key_label": DEFAULT_KEY_LABEL,
    "close_console_after": True,
    "auto_inject_on_load": True,
    "suppress_wolverine_warning": False,
    "show_splash": True,
}


class Settings:
    """Small dict-backed settings object with load/save."""

    def __init__(self, path: str = paths.SETTINGS_FILE):
        self.path = path
        self.data = dict(DEFAULTS)
        self.load()

    def load(self) -> None:
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as fh:
                    stored = json.load(fh)
                if isinstance(stored, dict):
                    # Keep only known keys, fill gaps with defaults.
                    self.data = {**DEFAULTS, **{k: stored[k] for k in DEFAULTS if k in stored}}
            except (json.JSONDecodeError, OSError):
                self.data = dict(DEFAULTS)

    def save(self) -> None:
        try:
            with open(self.path, "w", encoding="utf-8") as fh:
                json.dump(self.data, fh, indent=2)
        except OSError:
            pass  # settings are a convenience; never crash on a write failure

    def reset(self) -> None:
        self.data = dict(DEFAULTS)
        self.save()

    def __getitem__(self, key: str):
        return self.data.get(key, DEFAULTS.get(key))

    def __setitem__(self, key: str, value) -> None:
        self.data[key] = value
        self.save()

    def get(self, key: str, default=None):
        return self.data.get(key, default)
