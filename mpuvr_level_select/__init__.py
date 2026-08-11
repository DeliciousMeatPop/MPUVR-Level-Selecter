"""Marvel Powers United VR Level Select Tool.

A rewrite of the original DeliciousMeatPop / ARMGDDN Games tool that loads
Marvel Powers United VR levels through the Unreal console exposed by the
Universal Unreal Engine Unlocker (UUU) DLL.

Key differences from v1.0.x:
  * Injects the UUU DLL directly (native LoadLibrary injection) -- the UuuClient
    GUI is never launched.
  * Sends the console command by pasting it from the clipboard instead of typing
    it key-by-key, so it works on any keyboard layout (AZERTY, QWERTZ, etc.).
  * Opens the console by physical scancode, not by the '~' character.
  * All game/inject/load work runs on background threads, so the window never
    freezes.
"""

__version__ = "2.0.0"
__all__ = ["__version__"]
