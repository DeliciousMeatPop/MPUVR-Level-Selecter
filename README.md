# Marvel Powers United VR: Single Player Level Commands

A reference for loading Marvel Powers United VR levels directly via the Unreal
console, using the Universal Unreal Engine Unlocker (UUU). Useful for reaching
content that is otherwise locked behind matchmaking or cut from the retail
build.

> Requires a legitimate installed copy of the game. This only exposes the
> engine console that already ships with the title.

## Requirements

| Item | Notes |
| --- | --- |
| Marvel Powers United VR | PC build, `MarvelVR-Win64-Shipping.exe` |
| Universal Unreal Engine Unlocker | Available from [framedsc.com](https://framedsc.com/GeneralGuides/universal_ue4_consoleunlocker.htm) |
| A PCVR headset | Some levels render on the flat screen only, see notes below |

## Usage

1. Launch the game so that `MarvelVR-Win64-Shipping.exe` is running.
2. Launch the Universal Unreal Engine Unlocker.
3. Select the `MarvelVR-Win64-Shipping.exe` process and inject the DLL.
4. Click the Marvel Powers United window so it has keyboard focus.
5. Press `~`. A black console bar appears across the screen.
6. Type `open` followed by a level command, then press Enter.

Example:

```
open marketplace
```

That loads the Knowhere Marketplace.

## Level commands

| Command | Level |
| --- | --- |
| `menu` | Title screen, leads to the hub |
| `ops` | Hub |
| `starktower` | Tutorial intro sequence (playable as Captain America or Black Widow only) |
| `hangar` | X-Mansion Hangar |
| `marketplace` | Knowhere Marketplace |
| `throneroom` | Asgard |
| `jotunheim` | Jotunheim |
| `researchlab` | Wakanda |
| `forest` | Halfworld |
| `arena` | Sakaar Arena |
| `downtown` | Downtown New York |
| `void` | Dark Dimension |
| `palace` | Attilan |
| `sanctuaryii` | Sanctuary II (Thanos boss battle) |

## Development and debug levels

These load but are incomplete. Expect dead ends.

| Command | Level | Known issues |
| --- | --- | --- |
| `movetutorial` | Early movement tutorial | Ends on a placeholder after the turn, move, and menu lessons. No exit other than quitting. |
| `nick_testarena` | Early Danger Room training map | Renders on the PC monitor only, not in the headset. Units cannot be spawned. |
| `dangerroom03` | Danger Room training map | Renders on the PC monitor only, not in the headset. Units cannot be spawned. |
| `EndScreen_Retail_Jul_2018` | Retail demo end card | Displays the "available now" screen and ends the session. Built for show floor demos. |

## Notes

- Level commands are case insensitive apart from `EndScreen_Retail_Jul_2018`,
  which is safest typed exactly as written.
- The console closes on `~` or `Esc`. If input stops registering, click the game
  window again to restore focus.
- Injection has to be redone every time the game process restarts.

## Source

Transcribed from the community cheat sheet
"Marvel Powers United Single Player Cheat Sheet"
(<https://www.scribd.com/document/819204526/Marvel-Powers-United-Single-Player-Cheat-Sheet-Sheet1>).
