"""Coordinates game/inject/load actions off the UI thread.

The UI never calls Win32 directly. It calls these methods, which run the actual
work on a worker thread and report progress through a thread-safe queue of
``Event`` objects. The UI drains that queue on a timer, so it stays responsive
and never freezes -- unlike the original tool, which slept on the main thread.
"""

from __future__ import annotations

import queue
import threading
import time
from dataclasses import dataclass

from . import commands, injector
from .config import Settings
from .keys import by_label
from .levels import Level


@dataclass
class LogEvent:
    text: str
    level: str = "info"  # info | success | warn | error


@dataclass
class StateEvent:
    game_running: bool
    injected: bool
    pid: int | None


class Controller:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.events: "queue.Queue" = queue.Queue()

        self.pid: int | None = None
        self.injected: bool = False

        self._action_lock = threading.Lock()
        self._stop_poll = threading.Event()
        self._poller: threading.Thread | None = None

    # -- event helpers -------------------------------------------------------

    def _log(self, text: str, level: str = "info") -> None:
        self.events.put(LogEvent(text, level))

    def _emit_state(self) -> None:
        self.events.put(StateEvent(self.pid is not None, self.injected, self.pid))

    # -- background state polling -------------------------------------------

    def start_polling(self) -> None:
        if self._poller and self._poller.is_alive():
            return
        self._stop_poll.clear()
        self._poller = threading.Thread(target=self._poll_loop, daemon=True)
        self._poller.start()

    def stop_polling(self) -> None:
        self._stop_poll.set()

    def _poll_loop(self) -> None:
        while not self._stop_poll.wait(1.5):
            found = injector.find_game_pid()
            changed = False
            if found != self.pid:
                self.pid = found
                if found is None:
                    self.injected = False
                changed = True
            if self.pid is not None:
                # Confirm injection state opportunistically (best effort).
                loaded = injector.is_dll_loaded(self.pid)
                if loaded and not self.injected:
                    self.injected = True
                    changed = True
            if changed:
                self._emit_state()

    # -- action runner -------------------------------------------------------

    def _run(self, fn, busy_msg: str) -> None:
        def wrapper():
            if not self._action_lock.acquire(blocking=False):
                self._log("Busy with another action, please wait…", "warn")
                return
            try:
                fn()
            except Exception as exc:  # noqa: BLE001 - report, never crash the UI
                self._log(f"Error: {exc}", "error")
            finally:
                self._action_lock.release()
                self._emit_state()

        threading.Thread(target=wrapper, daemon=True).start()

    # -- actions -------------------------------------------------------------

    def start_or_restart_game(self) -> None:
        self._run(self._start_or_restart_game, "starting game")

    def _start_or_restart_game(self) -> None:
        if self.pid is not None:
            self._log("Closing the running game…", "info")
            injector.kill_game(self.pid)
            self.pid = None
            self.injected = False
            time.sleep(2)

        self._log("Starting Marvel Powers United VR…", "info")
        injector.launch_game()

        # Wait for the process to appear (bounded, unlike the old infinite loop).
        deadline = time.time() + 60
        while time.time() < deadline:
            found = injector.find_game_pid()
            if found:
                self.pid = found
                self._log(f"Game running (PID {found}). Give it a moment to reach the menu.",
                          "success")
                return
            time.sleep(1)
        self._log("Timed out waiting for the game process to start.", "error")

    def inject(self) -> None:
        self._run(self._inject, "injecting")

    def _inject(self) -> None:
        if self.pid is None:
            self.pid = injector.find_game_pid()
        if self.pid is None:
            self._log("Game is not running — start it first.", "error")
            return
        if self.injected or injector.is_dll_loaded(self.pid):
            self.injected = True
            self._log("UUU DLL is already injected.", "success")
            return
        self._log("Injecting UUU DLL directly (no UuuClient)…", "info")
        method = injector.inject(self.pid)
        self.injected = True
        self._log(f"UUU DLL injected via {method}. Console is ready.", "success")

    def _ensure_ready(self) -> bool:
        """Make sure the game is running and the DLL is injected.

        Returns True when a command can be sent. Logs and returns False
        otherwise. Auto-injects when the setting allows it.
        """
        if self.pid is None:
            self.pid = injector.find_game_pid()
        if self.pid is None:
            self._log("Game is not running — start it first.", "error")
            return False

        if not self.injected and not injector.is_dll_loaded(self.pid):
            if self.settings["auto_inject_on_load"]:
                self._log("Not injected yet — injecting now…", "info")
                method = injector.inject(self.pid)
                self.injected = True
                self._log(f"UUU DLL injected via {method}.", "success")
            else:
                self._log("DLL not injected — click Inject DLL first.", "error")
                return False
        else:
            self.injected = True
        return True

    def _send(self, command: str) -> None:
        console_key = by_label(self.settings["console_key_label"])
        commands.send_console_command(
            self.pid,
            command,
            console_key,
            close_console=self.settings["close_console_after"],
        )

    def load_level(self, level: Level) -> None:
        self._run(lambda: self._load_level(level), "loading level")

    def _load_level(self, level: Level) -> None:
        if not self._ensure_ready():
            return
        self._log(f"Loading '{level.name}'  ({level.command})…", "info")
        self._send(level.command)
        self._log(f"Sent '{level.command}'. If nothing happened, check the console key matches UUU.",
                  "success")

    def send_command(self, command: str) -> None:
        self._run(lambda: self._send_command(command), "sending command")

    def _send_command(self, command: str) -> None:
        command = command.strip()
        if not command:
            self._log("Enter a command first.", "warn")
            return
        if not self._ensure_ready():
            return
        self._log(f"Sending: {command}", "info")
        self._send(command)
        self._log(f"Sent: {command}", "success")

    def exit_game(self) -> None:
        self._run(self._exit_game, "exiting game")

    def _exit_game(self) -> None:
        if self.pid is None:
            self.pid = injector.find_game_pid()
        if self.pid is None:
            self._log("No game process to close.", "warn")
            return
        self._log("Closing the game…", "info")
        injector.kill_game(self.pid)
        self.pid = None
        self.injected = False
        self._log("Game closed.", "success")
