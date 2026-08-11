"""Handy non-level console commands.

These are general Unreal Engine 4 commands exposed through the same console the
level loader uses. Availability depends on the shipping build -- some may do
nothing in Marvel Powers United VR -- so they are offered as quick picks, not
promises. Anything can also be typed into the custom command box.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class QuickCommand:
    label: str
    command: str
    note: str = ""


QUICK_COMMANDS: list[QuickCommand] = [
    QuickCommand("Show FPS", "stat fps", "Frame-rate overlay."),
    QuickCommand("Show frame timings", "stat unit", "Game/draw/GPU millisecond breakdown."),
    QuickCommand("Hide all stats", "stat none", "Clears any stat overlay."),
    QuickCommand("Hi-res screenshot", "HighResShot 2",
                 "Saves a 2x screenshot under the game's Saved/Screenshots folder."),
    QuickCommand("Restart current level", "RestartLevel", "Reloads the map you are in."),
    QuickCommand("Pause", "pause", "Toggles pause (UUU also has its own pause hotkey)."),
    QuickCommand("Slow motion  50%", "slomo 0.5", "Half speed."),
    QuickCommand("Normal speed", "slomo 1", "Back to 100% speed."),
    QuickCommand("Fast  2x", "slomo 2", "Double speed."),
    QuickCommand("Quit game", "quit", "Closes the game from inside the engine."),
]

_BY_LABEL = {q.label: q for q in QUICK_COMMANDS}


def by_label(label: str) -> QuickCommand | None:
    return _BY_LABEL.get(label)
