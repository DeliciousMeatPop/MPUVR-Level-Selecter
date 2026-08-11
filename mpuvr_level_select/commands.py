"""Send a console command to the running, injected game.

The sequence, all via native input:
  1. Focus the game window.
  2. Open the UUU console with the configured key (scancode by default).
  3. Put the command on the clipboard and paste it (Ctrl+V) -- layout independent.
  4. Press Enter.
  5. Optionally close the console again.
"""

from __future__ import annotations

import time

from . import winapi
from .keys import ConsoleKey


class CommandError(RuntimeError):
    pass


def send_console_command(
    pid: int,
    command: str,
    console_key: ConsoleKey,
    *,
    close_console: bool = True,
    focus_delay: float = 0.35,
    open_delay: float = 0.20,
    paste_delay: float = 0.12,
) -> None:
    """Type ``command`` into the game's Unreal console and run it.

    Delays are deliberately conservative; the console needs a beat to appear and
    to accept the paste. They are small enough to feel instant to the user.
    """
    hwnd = winapi.find_main_window(pid)
    if hwnd is None:
        raise CommandError(
            "Could not find the game window. Is the game past the loading screen?"
        )

    winapi.focus_window(hwnd)
    time.sleep(focus_delay)

    # Open the console.
    console_key.send()
    time.sleep(open_delay)

    # Paste the command instead of typing it -- no per-character layout issues.
    winapi.set_clipboard_text(command)
    time.sleep(paste_delay)
    winapi.paste()
    time.sleep(paste_delay)

    winapi.press_enter()

    if close_console:
        time.sleep(open_delay)
        console_key.send()
