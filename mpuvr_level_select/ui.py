"""CustomTkinter UI for the level select tool."""

from __future__ import annotations

import webbrowser
from datetime import datetime
from tkinter import messagebox

import customtkinter as ctk

from . import __version__
from .config import Settings
from .controller import Controller, LogEvent, StateEvent
from .keys import CONSOLE_KEYS, by_label
from .levels import LEVELS, Level, categories, levels_in

GITHUB_URL = "https://github.com/DeliciousMeatPop"
TELEGRAM_URL = "https://t.me/ARMGDDNGames"
DISCORD_URL = "https://discord.com/invite/28fRTaTSd9"

# Palette
BG = "#1c1c1c"
CARD = "#242424"
ACCENT = "#3a7bd5"
LINK = "#4aa8ff"
LOG_COLORS = {
    "info": "#d0d0d0",
    "success": "#57d977",
    "warn": "#e8c15a",
    "error": "#ff6b6b",
}


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.settings = Settings()
        self.controller = Controller(self.settings)

        self.title("Marvel Powers United VR — Level Select Tool")
        self.geometry("880x860")
        self.minsize(760, 720)
        self.configure(fg_color=BG)

        self._level_buttons: list[tuple[Level, ctk.CTkButton]] = []

        self._build_header()
        self._build_status()
        self._build_actions()
        self._build_options()
        self._build_level_picker()
        self._build_log()
        self._build_footer()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self.controller.start_polling()
        self.after(100, self._pump_events)
        self._log_line("Ready. Start the game, then pick a level — injection is automatic.", "info")

    # -- layout --------------------------------------------------------------

    def _build_header(self) -> None:
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(16, 4))

        ctk.CTkLabel(
            header, text="Marvel Powers United VR",
            font=ctk.CTkFont(size=22, weight="bold"), text_color="#ffffff",
        ).pack(anchor="w")
        ctk.CTkLabel(
            header, text=f"Level Select Tool  v{__version__}",
            font=ctk.CTkFont(size=13), text_color=ACCENT,
        ).pack(anchor="w")

        btns = ctk.CTkFrame(header, fg_color="transparent")
        btns.place(relx=1.0, rely=0.5, anchor="e")
        ctk.CTkButton(btns, text="About", width=70, command=self._show_about).pack(side="left", padx=4)
        ctk.CTkButton(btns, text="Options", width=70, command=self._show_options).pack(side="left", padx=4)

    def _build_status(self) -> None:
        bar = ctk.CTkFrame(self, fg_color=CARD, corner_radius=10)
        bar.pack(fill="x", padx=20, pady=8)
        self.game_status = ctk.CTkLabel(bar, text="●  Game: checking…",
                                        font=ctk.CTkFont(size=13, weight="bold"))
        self.game_status.pack(side="left", padx=16, pady=10)
        self.inject_status = ctk.CTkLabel(bar, text="●  Injected: no",
                                          font=ctk.CTkFont(size=13, weight="bold"))
        self.inject_status.pack(side="left", padx=16, pady=10)

    def _build_actions(self) -> None:
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=4)
        ctk.CTkButton(row, text="Start / Restart Game",
                      command=self.controller.start_or_restart_game).pack(
            side="left", expand=True, fill="x", padx=(0, 4))
        ctk.CTkButton(row, text="Inject DLL",
                      command=self.controller.inject).pack(
            side="left", expand=True, fill="x", padx=4)
        ctk.CTkButton(row, text="Exit Game", fg_color="#5a2a2a", hover_color="#743636",
                      command=self.controller.exit_game).pack(
            side="left", expand=True, fill="x", padx=(4, 0))

    def _build_options(self) -> None:
        row = ctk.CTkFrame(self, fg_color=CARD, corner_radius=10)
        row.pack(fill="x", padx=20, pady=8)

        ctk.CTkLabel(row, text="Console key:", font=ctk.CTkFont(size=13)).pack(
            side="left", padx=(16, 6), pady=12)
        self.key_menu = ctk.CTkOptionMenu(
            row, values=[k.label for k in CONSOLE_KEYS], width=320,
            command=self._on_key_change,
        )
        self.key_menu.set(self.settings["console_key_label"])
        self.key_menu.pack(side="left", padx=6, pady=12)

        ctk.CTkLabel(
            row, text="must match the console key set in UUU",
            font=ctk.CTkFont(size=11), text_color="#9a9a9a",
        ).pack(side="left", padx=8)

    def _build_level_picker(self) -> None:
        wrap = ctk.CTkFrame(self, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=20, pady=(4, 8))

        top = ctk.CTkFrame(wrap, fg_color="transparent")
        top.pack(fill="x")
        ctk.CTkLabel(top, text="Choose a level",
                     font=ctk.CTkFont(size=15, weight="bold")).pack(side="left")
        self.search = ctk.CTkEntry(top, placeholder_text="Search levels…", width=240)
        self.search.pack(side="right")
        self.search.bind("<KeyRelease>", lambda _e: self._refilter())

        self.level_frame = ctk.CTkScrollableFrame(wrap, fg_color=CARD, corner_radius=10, height=240)
        self.level_frame.pack(fill="both", expand=True, pady=(8, 0))
        self._populate_levels()

    def _populate_levels(self) -> None:
        self._level_buttons.clear()
        for cat in categories():
            ctk.CTkLabel(
                self.level_frame, text=cat.upper(),
                font=ctk.CTkFont(size=11, weight="bold"), text_color=ACCENT,
            ).pack(anchor="w", padx=10, pady=(10, 2))
            for level in levels_in(cat):
                label = level.name if not level.subtitle else f"{level.name}   ·   {level.subtitle}"
                btn = ctk.CTkButton(
                    self.level_frame, text=label, anchor="w", height=34,
                    fg_color="#2f2f2f", hover_color=ACCENT,
                    command=lambda lvl=level: self._on_level_click(lvl),
                )
                btn.pack(fill="x", padx=8, pady=2)
                self._level_buttons.append((level, btn))

    def _refilter(self) -> None:
        query = self.search.get().strip().lower()
        for level, btn in self._level_buttons:
            if not query or query in level.search_text:
                btn.pack(fill="x", padx=8, pady=2)
            else:
                btn.pack_forget()

    def _build_log(self) -> None:
        wrap = ctk.CTkFrame(self, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=20, pady=(0, 8))
        ctk.CTkLabel(wrap, text="Activity log",
                     font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w")
        self.log_box = ctk.CTkTextbox(wrap, fg_color="#161616", corner_radius=10, height=170,
                                      font=ctk.CTkFont(family="Consolas", size=12))
        self.log_box.pack(fill="both", expand=True, pady=(6, 0))
        self.log_box.configure(state="disabled")
        for name, color in LOG_COLORS.items():
            try:
                self.log_box.tag_config(name, foreground=color)
            except Exception:  # noqa: BLE001 - tag support varies; degrade gracefully
                pass

    def _build_footer(self) -> None:
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(fill="x", padx=20, pady=(0, 14))

        ctk.CTkButton(footer, text="Exit Tool", width=90, fg_color="#333333",
                      hover_color="#444444", command=self._on_close).pack(side="right")

        credit = ctk.CTkFrame(footer, fg_color="transparent")
        credit.pack(side="left")
        self._credit_part(credit, "Made with ")
        self._credit_part(credit, "❤️", color="#ff5a5a")
        self._credit_part(credit, " by ")
        self._credit_link(credit, "DMP", GITHUB_URL)
        self._credit_part(credit, " of ")
        self._credit_link(credit, "ARMGDDN Games", TELEGRAM_URL)

    def _credit_part(self, parent, text, color="#c0c0c0") -> None:
        ctk.CTkLabel(parent, text=text, font=ctk.CTkFont(size=12), text_color=color).pack(side="left")

    def _credit_link(self, parent, text, url) -> None:
        link = ctk.CTkLabel(parent, text=text, font=ctk.CTkFont(size=12, weight="bold"),
                            text_color=LINK, cursor="hand2")
        link.pack(side="left")
        link.bind("<Button-1>", lambda _e, u=url: webbrowser.open_new(u))

    # -- event handling ------------------------------------------------------

    def _pump_events(self) -> None:
        try:
            while True:
                event = self.controller.events.get_nowait()
                if isinstance(event, LogEvent):
                    self._log_line(event.text, event.level)
                elif isinstance(event, StateEvent):
                    self._apply_state(event)
        except Exception:  # queue.Empty and any transient UI error
            pass
        self.after(120, self._pump_events)

    def _apply_state(self, state: StateEvent) -> None:
        if state.game_running:
            self.game_status.configure(text=f"●  Game: running (PID {state.pid})",
                                       text_color=LOG_COLORS["success"])
        else:
            self.game_status.configure(text="●  Game: not running", text_color="#9a9a9a")
        if state.injected:
            self.inject_status.configure(text="●  Injected: yes", text_color=LOG_COLORS["success"])
        else:
            self.inject_status.configure(text="●  Injected: no", text_color="#e8c15a")

    def _log_line(self, text: str, level: str = "info") -> None:
        stamp = datetime.now().strftime("%H:%M:%S")
        self.log_box.configure(state="normal")
        try:
            self.log_box.insert("end", f"{stamp}  {text}\n", level)
        except Exception:  # noqa: BLE001 - fall back to untagged insert
            self.log_box.insert("end", f"{stamp}  {text}\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    # -- user actions --------------------------------------------------------

    def _on_key_change(self, label: str) -> None:
        self.settings["console_key_label"] = label
        key = by_label(label)
        note = f" — {key.note}" if key.note else ""
        self._log_line(f"Console key set to: {label}{note}", "success")

    def _on_level_click(self, level: Level) -> None:
        if level.warning and not self.settings["suppress_wolverine_warning"]:
            if not messagebox.askokcancel("Heads up", level.warning, icon="warning"):
                return
        self.controller.load_level(level)

    def _on_close(self) -> None:
        self.controller.stop_polling()
        self.destroy()

    # -- dialogs -------------------------------------------------------------

    def _show_about(self) -> None:
        win = ctk.CTkToplevel(self)
        win.title("About")
        win.geometry("420x300")
        win.configure(fg_color=BG)
        win.transient(self)
        win.after(100, win.lift)

        ctk.CTkLabel(win, text="Marvel Powers United VR\nLevel Select Tool",
                     font=ctk.CTkFont(size=18, weight="bold"), justify="center").pack(pady=(20, 6))
        ctk.CTkLabel(win, text=f"v{__version__}", text_color=ACCENT).pack()
        ctk.CTkLabel(
            win,
            text="Made by DeliciousMeatPop (DMP) of ARMGDDN Games\n"
                 "for the Marvel Powers United VR Revival community.",
            justify="center", wraplength=380, text_color="#c8c8c8",
        ).pack(pady=14)

        links = ctk.CTkFrame(win, fg_color="transparent")
        links.pack(pady=6)
        ctk.CTkButton(links, text="GitHub (DMP)", width=120,
                      command=lambda: webbrowser.open_new(GITHUB_URL)).pack(side="left", padx=5)
        ctk.CTkButton(links, text="ARMGDDN Telegram", width=140,
                      command=lambda: webbrowser.open_new(TELEGRAM_URL)).pack(side="left", padx=5)
        ctk.CTkButton(win, text="MPUVR Revival Discord", width=200,
                      command=lambda: webbrowser.open_new(DISCORD_URL)).pack(pady=6)

    def _show_options(self) -> None:
        win = ctk.CTkToplevel(self)
        win.title("Options")
        win.geometry("420x280")
        win.configure(fg_color=BG)
        win.transient(self)
        win.after(100, win.lift)

        auto = ctk.BooleanVar(value=bool(self.settings["auto_inject_on_load"]))
        close_c = ctk.BooleanVar(value=bool(self.settings["close_console_after"]))
        supp = ctk.BooleanVar(value=bool(self.settings["suppress_wolverine_warning"]))

        def bind(var, key):
            self.settings[key] = bool(var.get())

        ctk.CTkLabel(win, text="Options", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(18, 10))
        ctk.CTkCheckBox(win, text="Auto-inject the DLL when loading a level",
                        variable=auto, command=lambda: bind(auto, "auto_inject_on_load")).pack(
            anchor="w", padx=30, pady=6)
        ctk.CTkCheckBox(win, text="Close the console after sending the command",
                        variable=close_c, command=lambda: bind(close_c, "close_console_after")).pack(
            anchor="w", padx=30, pady=6)
        ctk.CTkCheckBox(win, text="Skip the Wolverine reminder",
                        variable=supp, command=lambda: bind(supp, "suppress_wolverine_warning")).pack(
            anchor="w", padx=30, pady=6)

        ctk.CTkButton(win, text="Reset all settings to default",
                      fg_color="#5a2a2a", hover_color="#743636",
                      command=lambda: self._reset_settings(win)).pack(pady=18)

    def _reset_settings(self, win) -> None:
        self.settings.reset()
        self.key_menu.set(self.settings["console_key_label"])
        self._log_line("Settings reset to default.", "success")
        win.destroy()


def main() -> None:
    app = App()
    app.mainloop()
