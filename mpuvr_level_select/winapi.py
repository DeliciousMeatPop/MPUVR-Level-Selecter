"""Thin ctypes wrapper around the Win32 APIs the tool needs.

Everything here is Windows-only. Functions are deliberately small and free of
GUI/state so they can be unit-reasoned about in isolation.

The two things that make this reliable where the old PowerShell ``SendKeys``
approach was not:

  * Keys are sent with ``SendInput`` using **scancodes** (physical keys) for the
    console toggle, so the console opens regardless of keyboard layout.
  * The command text is placed on the clipboard and pasted with Ctrl+V rather
    than typed, so no character is ever mistyped on a non-QWERTY layout.
"""

from __future__ import annotations

import ctypes
from ctypes import wintypes

user32 = ctypes.WinDLL("user32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

# ULONG_PTR is pointer-sized; getting this wrong truncates dwExtraInfo on x64.
ULONG_PTR = ctypes.c_uint64 if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_uint32

# ---------------------------------------------------------------------------
# SendInput structures
# ---------------------------------------------------------------------------

INPUT_KEYBOARD = 1
KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004
KEYEVENTF_SCANCODE = 0x0008

# Virtual key codes we use by name.
VK_CONTROL = 0x11
VK_RETURN = 0x0D
VK_V = 0x56


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg", wintypes.DWORD),
        ("wParamL", wintypes.WORD),
        ("wParamH", wintypes.WORD),
    ]


class _INPUTunion(ctypes.Union):
    _fields_ = [("ki", KEYBDINPUT), ("mi", MOUSEINPUT), ("hi", HARDWAREINPUT)]


class INPUT(ctypes.Structure):
    _fields_ = [("type", wintypes.DWORD), ("u", _INPUTunion)]


user32.SendInput.argtypes = (wintypes.UINT, ctypes.POINTER(INPUT), ctypes.c_int)
user32.SendInput.restype = wintypes.UINT


def _kbd_input(*, vk: int = 0, scan: int = 0, flags: int = 0) -> INPUT:
    return INPUT(
        type=INPUT_KEYBOARD,
        u=_INPUTunion(ki=KEYBDINPUT(wVk=vk, wScan=scan, dwFlags=flags, time=0, dwExtraInfo=0)),
    )


def _send(inputs: list[INPUT]) -> None:
    n = len(inputs)
    arr = (INPUT * n)(*inputs)
    sent = user32.SendInput(n, arr, ctypes.sizeof(INPUT))
    if sent != n:
        raise ctypes.WinError(ctypes.get_last_error())


def tap_scancode(scan: int, *, extended: bool = False) -> None:
    """Press and release a physical key identified by its scancode."""
    base = KEYEVENTF_SCANCODE | (KEYEVENTF_EXTENDEDKEY if extended else 0)
    _send(
        [
            _kbd_input(scan=scan, flags=base),
            _kbd_input(scan=scan, flags=base | KEYEVENTF_KEYUP),
        ]
    )


def tap_vk(vk: int, *, extended: bool = False) -> None:
    """Press and release a key identified by its virtual-key code."""
    down = KEYEVENTF_EXTENDEDKEY if extended else 0
    _send(
        [
            _kbd_input(vk=vk, flags=down),
            _kbd_input(vk=vk, flags=down | KEYEVENTF_KEYUP),
        ]
    )


def press_enter() -> None:
    tap_vk(VK_RETURN)


def paste() -> None:
    """Send Ctrl+V."""
    _send(
        [
            _kbd_input(vk=VK_CONTROL),
            _kbd_input(vk=VK_V),
            _kbd_input(vk=VK_V, flags=KEYEVENTF_KEYUP),
            _kbd_input(vk=VK_CONTROL, flags=KEYEVENTF_KEYUP),
        ]
    )


# ---------------------------------------------------------------------------
# Clipboard (CF_UNICODETEXT)
# ---------------------------------------------------------------------------

CF_UNICODETEXT = 13
GMEM_MOVEABLE = 0x0002

kernel32.GlobalAlloc.restype = wintypes.HGLOBAL
kernel32.GlobalAlloc.argtypes = [wintypes.UINT, ctypes.c_size_t]
kernel32.GlobalLock.restype = wintypes.LPVOID
kernel32.GlobalLock.argtypes = [wintypes.HGLOBAL]
kernel32.GlobalUnlock.argtypes = [wintypes.HGLOBAL]
user32.OpenClipboard.argtypes = [wintypes.HWND]
user32.SetClipboardData.restype = wintypes.HANDLE
user32.SetClipboardData.argtypes = [wintypes.UINT, wintypes.HANDLE]


def set_clipboard_text(text: str) -> None:
    """Replace the clipboard contents with ``text`` (UTF-16)."""
    if not user32.OpenClipboard(None):
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        user32.EmptyClipboard()
        data = text.encode("utf-16-le") + b"\x00\x00"
        handle = kernel32.GlobalAlloc(GMEM_MOVEABLE, len(data))
        if not handle:
            raise ctypes.WinError(ctypes.get_last_error())
        ptr = kernel32.GlobalLock(handle)
        if not ptr:
            raise ctypes.WinError(ctypes.get_last_error())
        try:
            ctypes.memmove(ptr, data, len(data))
        finally:
            kernel32.GlobalUnlock(handle)
        if not user32.SetClipboardData(CF_UNICODETEXT, handle):
            raise ctypes.WinError(ctypes.get_last_error())
        # Ownership of the memory has passed to the clipboard; do not free it.
    finally:
        user32.CloseClipboard()


# ---------------------------------------------------------------------------
# Window focus
# ---------------------------------------------------------------------------

SW_RESTORE = 9

WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
user32.EnumWindows.argtypes = [WNDENUMPROC, wintypes.LPARAM]
user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
user32.GetWindowThreadProcessId.restype = wintypes.DWORD
user32.IsWindowVisible.argtypes = [wintypes.HWND]
user32.GetForegroundWindow.restype = wintypes.HWND
user32.AttachThreadInput.argtypes = [wintypes.DWORD, wintypes.DWORD, wintypes.BOOL]
user32.SetForegroundWindow.argtypes = [wintypes.HWND]
user32.BringWindowToTop.argtypes = [wintypes.HWND]
user32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
kernel32.GetCurrentThreadId.restype = wintypes.DWORD


def find_main_window(pid: int) -> int | None:
    """Return the handle of a visible top-level window owned by ``pid``."""
    result: list[int] = []

    @WNDENUMPROC
    def _callback(hwnd, _lparam):
        wnd_pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(wnd_pid))
        if wnd_pid.value == pid and user32.IsWindowVisible(hwnd):
            result.append(hwnd)
            return False  # stop enumeration
        return True

    user32.EnumWindows(_callback, 0)
    return result[0] if result else None


def focus_window(hwnd: int) -> None:
    """Force ``hwnd`` to the foreground with the AttachThreadInput dance.

    SetForegroundWindow is rate/focus limited by Windows; attaching our input
    queue to the target window's thread lets the call succeed reliably.
    """
    user32.ShowWindow(hwnd, SW_RESTORE)
    fg = user32.GetForegroundWindow()
    target_thread = user32.GetWindowThreadProcessId(hwnd, None)
    fg_thread = user32.GetWindowThreadProcessId(fg, None) if fg else 0
    current_thread = kernel32.GetCurrentThreadId()

    attached_target = attached_fg = False
    if target_thread and target_thread != current_thread:
        attached_target = bool(user32.AttachThreadInput(current_thread, target_thread, True))
    if fg_thread and fg_thread not in (current_thread, target_thread):
        attached_fg = bool(user32.AttachThreadInput(current_thread, fg_thread, True))
    try:
        user32.BringWindowToTop(hwnd)
        user32.SetForegroundWindow(hwnd)
    finally:
        if attached_target:
            user32.AttachThreadInput(current_thread, target_thread, False)
        if attached_fg:
            user32.AttachThreadInput(current_thread, fg_thread, False)
