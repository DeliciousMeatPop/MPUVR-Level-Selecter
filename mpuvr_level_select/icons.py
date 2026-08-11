"""Resolve the application icon.

Your own ``MPUVR.ico`` dropped next to the tool always wins; a generated icon
in ``assets/`` is the fallback so the app is never icon-less.
"""

from __future__ import annotations

import os

from . import paths

# Checked in order; first existing file wins.
_ICO_CANDIDATES = [
    paths.resource("MPUVR.ico"),
    paths.resource("assets", "MPUVR.ico"),
    paths.resource("assets", "mpuvr.ico"),
]
_PNG_CANDIDATES = [
    paths.resource("MPUVR.png"),
    paths.resource("assets", "MPUVR.png"),
    paths.resource("assets", "mpuvr.png"),
]
_SPLASH_CANDIDATES = [
    paths.resource("splash.png"),
    paths.resource("MPUVR_splash.png"),
    paths.resource("assets", "splash.png"),
    paths.resource("assets", "MPUVR_splash.png"),
]


def _first_existing(candidates: list[str]) -> str | None:
    for path in candidates:
        if os.path.exists(path):
            return path
    return None


def icon_ico() -> str | None:
    """Path to a .ico for the title bar / taskbar (Windows), or None."""
    return _first_existing(_ICO_CANDIDATES)


def icon_png() -> str | None:
    """Path to a .png for tkinter's iconphoto fallback, or None."""
    return _first_existing(_PNG_CANDIDATES)


def splash_png() -> str | None:
    """Path to the startup splash image (PNG), or None.

    A user-supplied ``splash.png`` (root or assets/) wins over the generated one.
    """
    return _first_existing(_SPLASH_CANDIDATES)
