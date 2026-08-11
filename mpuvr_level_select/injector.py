"""Process management and DLL injection.

Injection is done natively (``LoadLibraryW`` via ``CreateRemoteThread``) so the
UuuClient GUI is never involved -- only the ``UniversalUE4Unlocker.dll`` is
loaded into the game. If native injection fails for some reason, the bundled
``Injector.exe`` is used as a fallback.
"""

from __future__ import annotations

import ctypes
import os
import subprocess
from ctypes import wintypes

import psutil

from . import paths

kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

# ---------------------------------------------------------------------------
# Win32 signatures (restypes matter on x64 -- a default int truncates handles)
# ---------------------------------------------------------------------------

PROCESS_ALL_ACCESS = 0x1F0FFF
MEM_COMMIT = 0x1000
MEM_RESERVE = 0x2000
MEM_RELEASE = 0x8000
PAGE_READWRITE = 0x04
WAIT_TIMEOUT = 0x102

kernel32.OpenProcess.restype = wintypes.HANDLE
kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
kernel32.VirtualAllocEx.restype = wintypes.LPVOID
kernel32.VirtualAllocEx.argtypes = [
    wintypes.HANDLE, wintypes.LPVOID, ctypes.c_size_t, wintypes.DWORD, wintypes.DWORD,
]
kernel32.VirtualFreeEx.argtypes = [
    wintypes.HANDLE, wintypes.LPVOID, ctypes.c_size_t, wintypes.DWORD,
]
kernel32.WriteProcessMemory.argtypes = [
    wintypes.HANDLE, wintypes.LPVOID, wintypes.LPCVOID, ctypes.c_size_t,
    ctypes.POINTER(ctypes.c_size_t),
]
kernel32.GetModuleHandleW.restype = wintypes.HMODULE
kernel32.GetModuleHandleW.argtypes = [wintypes.LPCWSTR]
kernel32.GetProcAddress.restype = ctypes.c_void_p
kernel32.GetProcAddress.argtypes = [wintypes.HMODULE, wintypes.LPCSTR]
kernel32.CreateRemoteThread.restype = wintypes.HANDLE
kernel32.CreateRemoteThread.argtypes = [
    wintypes.HANDLE, wintypes.LPVOID, ctypes.c_size_t, wintypes.LPVOID,
    wintypes.LPVOID, wintypes.DWORD, wintypes.LPVOID,
]
kernel32.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
kernel32.WaitForSingleObject.restype = wintypes.DWORD
kernel32.GetExitCodeThread.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
kernel32.CloseHandle.argtypes = [wintypes.HANDLE]


class InjectionError(RuntimeError):
    """Raised when the DLL could not be injected."""


# ---------------------------------------------------------------------------
# Process helpers
# ---------------------------------------------------------------------------


def find_game_pid(process_name: str = paths.GAME_PROCESS_NAME) -> int | None:
    """Return the PID of the running game, or None."""
    for proc in psutil.process_iter(["name", "pid"]):
        try:
            if proc.info["name"] and proc.info["name"].lower() == process_name.lower():
                return proc.info["pid"]
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return None


def launch_game(game_exe: str = paths.GAME_EXE) -> None:
    """Start the game executable."""
    if not os.path.exists(game_exe):
        raise FileNotFoundError(game_exe)
    subprocess.Popen([game_exe], cwd=os.path.dirname(game_exe))


def kill_game(pid: int) -> None:
    """Terminate the game process (and children)."""
    try:
        proc = psutil.Process(pid)
    except psutil.NoSuchProcess:
        return
    for child in proc.children(recursive=True):
        _safe_terminate(child)
    _safe_terminate(proc)


def _safe_terminate(proc: "psutil.Process") -> None:
    try:
        proc.terminate()
        proc.wait(timeout=5)
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass
    except psutil.TimeoutExpired:
        try:
            proc.kill()
        except psutil.NoSuchProcess:
            pass


def is_dll_loaded(pid: int, dll_name: str = "UniversalUE4Unlocker.dll") -> bool:
    """Best-effort check whether the UUU DLL is already loaded in ``pid``.

    Uses psutil's ``memory_maps`` which lists the process's loaded modules on
    Windows. Returns False if the information cannot be read (e.g. permission),
    so callers should treat a False as "unknown / not confirmed", not proof.
    """
    try:
        proc = psutil.Process(pid)
        for mmap in proc.memory_maps():
            if os.path.basename(mmap.path).lower() == dll_name.lower():
                return True
    except (psutil.NoSuchProcess, psutil.AccessDenied, OSError):
        pass
    return False


# ---------------------------------------------------------------------------
# Injection
# ---------------------------------------------------------------------------


def inject_native(pid: int, dll_path: str = paths.UUU_DLL) -> None:
    """Inject ``dll_path`` into ``pid`` via LoadLibraryW in a remote thread."""
    dll_path = os.path.abspath(dll_path)
    if not os.path.exists(dll_path):
        raise FileNotFoundError(dll_path)

    handle = kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
    if not handle:
        raise InjectionError(
            f"OpenProcess failed (err {ctypes.get_last_error()}). "
            "Try running the tool as Administrator."
        )

    remote_mem = None
    try:
        encoded = dll_path.encode("utf-16-le") + b"\x00\x00"
        size = len(encoded)
        remote_mem = kernel32.VirtualAllocEx(
            handle, None, size, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE
        )
        if not remote_mem:
            raise InjectionError(f"VirtualAllocEx failed (err {ctypes.get_last_error()}).")

        written = ctypes.c_size_t(0)
        ok = kernel32.WriteProcessMemory(
            handle, remote_mem, encoded, size, ctypes.byref(written)
        )
        if not ok or written.value != size:
            raise InjectionError(f"WriteProcessMemory failed (err {ctypes.get_last_error()}).")

        h_kernel32 = kernel32.GetModuleHandleW("kernel32.dll")
        load_library = kernel32.GetProcAddress(h_kernel32, b"LoadLibraryW")
        if not load_library:
            raise InjectionError("Could not resolve LoadLibraryW address.")

        thread = kernel32.CreateRemoteThread(
            handle, None, 0, load_library, remote_mem, 0, None
        )
        if not thread:
            raise InjectionError(f"CreateRemoteThread failed (err {ctypes.get_last_error()}).")
        try:
            if kernel32.WaitForSingleObject(thread, 15000) == WAIT_TIMEOUT:
                raise InjectionError("Injection thread timed out.")
            exit_code = wintypes.DWORD(0)
            kernel32.GetExitCodeThread(thread, ctypes.byref(exit_code))
            # LoadLibraryW returns the module handle (non-zero) on success. On
            # x64 the 64-bit HMODULE is truncated to the 32-bit thread exit
            # code, so a zero here means failure; non-zero means success.
            if exit_code.value == 0:
                raise InjectionError(
                    "LoadLibraryW returned NULL inside the game -- the DLL path "
                    "may be wrong or the DLL failed to load."
                )
        finally:
            kernel32.CloseHandle(thread)
    finally:
        if remote_mem:
            kernel32.VirtualFreeEx(handle, remote_mem, 0, MEM_RELEASE)
        kernel32.CloseHandle(handle)


def inject_via_exe(pid: int, dll_path: str = paths.UUU_DLL,
                   injector_exe: str = paths.INJECTOR_EXE) -> None:
    """Fallback: inject using the bundled Injector.exe."""
    if not os.path.exists(injector_exe):
        raise FileNotFoundError(injector_exe)
    if not os.path.exists(dll_path):
        raise FileNotFoundError(dll_path)
    startup = subprocess.STARTUPINFO()
    startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW  # keep the console hidden
    subprocess.run(
        [injector_exe, "--process-id", str(pid), "--inject", os.path.abspath(dll_path)],
        check=True,
        startupinfo=startup,
    )


def inject(pid: int, dll_path: str = paths.UUU_DLL) -> str:
    """Inject the UUU DLL, preferring the native path.

    Returns a short string describing which method succeeded. Raises
    InjectionError if both approaches fail.
    """
    try:
        inject_native(pid, dll_path)
        return "native"
    except (InjectionError, FileNotFoundError, OSError) as native_err:
        try:
            inject_via_exe(pid, dll_path)
            return "Injector.exe"
        except Exception as exe_err:  # noqa: BLE001 - surface both causes
            raise InjectionError(
                f"Native injection failed ({native_err}); "
                f"Injector.exe fallback also failed ({exe_err})."
            ) from exe_err
