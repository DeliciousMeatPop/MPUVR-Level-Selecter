# Marvel Powers United VR — Level Select Tool

<p align="center">
  <img src="https://github.com/user-attachments/assets/7a189bf8-9dee-43a7-9f57-58549ef8bcbb" alt="Jah-Yee Grammar Police" width="700">
</p>

---

A rewrite of the ARMGDDN Games level-select tool. It launches Marvel Powers
United VR, injects the Universal Unreal Engine Unlocker (UUU) DLL **directly**
(no UuuClient GUI), and loads any level through the Unreal console — including
content locked behind matchmaking or cut from the retail build.

> Requires a legitimate installed copy of the game. This only drives the engine
> console that already ships with the title.

Made with ❤️ by [DMP](https://github.com/DeliciousMeatPop) of
[ARMGDDN Games](https://t.me/ARMGDDNGames), for the
Marvel Powers United VR Revival community (originally, the project is now defunct after a DCMA from meta over the game files).

## What changed vs. v1.0.x

| Old behavior | New behavior |
| --- | --- |
| Launched `UuuClient.exe` (minimized) to inject | Injects `UniversalUE4Unlocker.dll` directly via native `LoadLibrary` — **the UUU GUI is never opened**. Falls back to the bundled `Injector.exe` if needed. |
| Typed the command key-by-key with PowerShell `SendKeys` | **Pastes** the command from the clipboard (Ctrl+V) — works on **any keyboard layout** (AZERTY / QWERTZ / etc.). No character is ever mistyped. |
| Opened the console by sending the `~` character (broken on non-US layouts, and `SendKeys` treats `~` as Enter) | Opens the console by **physical key (scancode)**, or a layout-independent key (F10, Insert, …) you pick from a list. |
| Ran everything on the UI thread — the window froze | All work runs on background threads; the window stays responsive with a live status bar and colored activity log. |
| Plain Tkinter look | Modern dark CustomTkinter UI with a searchable, categorized level list. |

## Layout

Drop the tool into the game folder, next to these (same as the original):

```
<game folder>/
├─ MPUVR Level Select Tool.exe        (or: run.py)
├─ WindowsNoEditor/MarvelVR/Binaries/Win64/MarvelVR-Win64-Shipping.exe
└─ InjectUUU/
   ├─ UniversalUE4Unlocker.dll        (required — this is what gets injected)
   └─ Injector.exe                    (optional fallback injector)
```

## Usage
0. This game has always had issues with VD, and oculus headsets are most likely to work. Link or airlink with gammon for rift next to the shipping exe is REQUIRED.
1. Click **Start / Restart Game** (or launch the game yourself — the tool
   auto-detects it).
2. Pick a level. That's it — the DLL is injected automatically on first load.
3. If a level doesn't load, make sure the **Console key** in the tool matches the
   console key configured in UUU (retail default is the backtick/tilde key, which
   is also the tool's default).

The **Inject DLL** and **Exit Game** buttons are there if you want manual control.

### Console key & non-QWERTY keyboards

The backtick/tilde option is sent by *physical key position*, so it works even on
layouts where `~` needs Shift or lives elsewhere. If that key does something else
on your keyboard, set UUU's console key to something universal (e.g. **F10** or
**Insert**) and pick the matching entry in the tool. The command text itself is
always pasted, never typed, so level names never come out garbled.

## Level commands

| Level | Command |
| --- | --- |
| Game Menu | `open menu` |
| Ops — Hub | `open Ops` |
| Stark Tower (tutorial intro) | `open StarkTower` |
| Hangar — X-Mansion Hangar | `open Hangar` |
| Marketplace — Knowhere | `open Marketplace` |
| Throne Room — Asgard | `open ThroneRoom` |
| Jotunheim | `open Jotunheim` |
| Research Lab — Wakanda | `open ResearchLab` |
| Forest — Halfworld | `open Forest` |
| Arena — Sakaar | `open Arena` |
| Downtown — New York | `open DownTown` |
| Void — Dark Dimension | `open Void` |
| Palace — Attilan | `open Palace` |
| Sanctuary II — Thanos boss | `open SanctuaryII` |
| Danger Room (needs Wolverine) | `open DangerRoom03` |
| Nick Test Arena (needs Wolverine) | `open Nick_TestArena` |
| Move Tutorial (debug) | `open MoveTutorial` |

Danger Room and Nick Test Arena require you to select **Wolverine** in the Hub
first; the tool reminds you before loading them.

## Extra console commands

The **Advanced console** section can send *any* console command through the same
reliable clipboard-paste path — either type it in the box (e.g. `stat fps`) and
press Enter, or use the quick-pick menu. These are general Unreal Engine 4
commands, so availability depends on the shipping build; treat them as things to
try, not guarantees.

| Quick pick | Command | Does |
| --- | --- | --- |
| Show FPS | `stat fps` | Frame-rate overlay |
| Show frame timings | `stat unit` | Game / draw / GPU millisecond breakdown |
| Hide all stats | `stat none` | Clears the overlay |
| Hi-res screenshot | `HighResShot 2` | Saves a 2× screenshot to the game's `Saved/Screenshots` |
| Restart current level | `RestartLevel` | Reloads the current map |
| Pause | `pause` | Toggles pause |
| Slow motion 50% / 2× | `slomo 0.5` / `slomo 2` | Game speed |
| Quit game | `quit` | Closes the game from the engine |

## App icon

The window and taskbar icon use `MPUVR.ico` if you drop one next to the tool
(or into `assets/`); otherwise a generated `assets/mpuvr.ico` is used. The icon
shows even when running from source (`python run.py`), and `build.bat` bakes it
into the `.exe`.

## Splash screen

On startup the tool shows a splash for a couple of seconds (click it to skip).
It uses `splash.png` if you drop one next to the tool (or into `assets/`) —
otherwise a generated `assets/splash.png` is used. The splash window is sized to
the image, so make your `splash.png` the size you want it shown. Turn it off any
time via **Options → Show splash screen on startup**.

## Notes

- Injection is redone automatically whenever the game process restarts.
- Native injection may need the tool to be run **as Administrator** on some
  systems; if native injection fails, it automatically retries with
  `Injector.exe`.
- `settings.json` and `levelselectscript.log` are written next to the tool.
