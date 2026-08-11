"""Console-toggle key presets.

The Universal Unreal Engine Unlocker opens the in-game console with a key you
configure. The retail default is the backtick / tilde key. On US QWERTY that key
sits left of ``1``; on many non-US layouts the ``~`` *character* lives elsewhere
or needs Shift, which is exactly why the original tool's "type a ~ character"
approach failed for those users.

We sidestep that by sending the **physical** key (a scancode) for the backtick
option, and by offering function/navigation keys whose virtual-key codes are the
same on every layout. Whichever you pick here must match the console key set in
UUU (the retail default is backtick, so that is our default too).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ConsoleKey:
    label: str          # shown in the UI
    mode: str           # "scancode" or "vk"
    code: int           # scancode or virtual-key code
    extended: bool = False
    note: str = ""

    def send(self) -> None:
        # Imported lazily so this module stays importable off-Windows.
        from . import winapi

        if self.mode == "scancode":
            winapi.tap_scancode(self.code, extended=self.extended)
        else:
            winapi.tap_vk(self.code, extended=self.extended)


# Ordered for the dropdown; the first entry is the default.
CONSOLE_KEYS: list[ConsoleKey] = [
    ConsoleKey("Backtick / Tilde  (`)  — UUU default", "scancode", 0x29,
               note="Physical key left of '1'. Works on any layout because it is sent by position."),
    ConsoleKey("F10", "vk", 0x79),
    ConsoleKey("F11", "vk", 0x7A),
    ConsoleKey("F8", "vk", 0x77),
    ConsoleKey("Insert", "vk", 0x2D, extended=True),
    ConsoleKey("Home", "vk", 0x24, extended=True),
    ConsoleKey("Page Up", "vk", 0x21, extended=True),
    ConsoleKey("Numpad *", "vk", 0x6A),
    ConsoleKey("Backslash  (\\)", "scancode", 0x2B,
               note="Physical key sent by position."),
]

DEFAULT_KEY_LABEL = CONSOLE_KEYS[0].label

_BY_LABEL = {k.label: k for k in CONSOLE_KEYS}


def by_label(label: str) -> ConsoleKey:
    """Look up a preset by its label, falling back to the default."""
    return _BY_LABEL.get(label, CONSOLE_KEYS[0])
