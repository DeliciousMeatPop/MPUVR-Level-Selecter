"""Filesystem path helpers.

The tool is meant to be dropped into the game folder (next to the
``WindowsNoEditor`` and ``InjectUUU`` directories) and run either as a plain
Python script or as a PyInstaller ``--onedir`` / ``--onefile`` build.
"""

from __future__ import annotations

import os
import sys


def base_path() -> str:
    """Directory the tool lives in.

    For a frozen (PyInstaller) build this is the folder containing the .exe;
    for a normal run it is the project root (one level up from this package).
    """
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def resource(*parts: str) -> str:
    """Absolute path to a resource next to the tool."""
    return os.path.join(base_path(), *parts)


# Well-known locations, matching the original tool's layout.
GAME_EXE = resource(
    "WindowsNoEditor", "MarvelVR", "Binaries", "Win64", "MarvelVR-Win64-Shipping.exe"
)
GAME_PROCESS_NAME = "MarvelVR-Win64-Shipping.exe"

UUU_DLL = resource("InjectUUU", "UniversalUE4Unlocker.dll")
INJECTOR_EXE = resource("InjectUUU", "Injector.exe")

SETTINGS_FILE = resource("settings.json")
LOG_FILE = resource("levelselectscript.log")
