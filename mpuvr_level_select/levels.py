"""The Marvel Powers United VR level catalog.

Commands are taken verbatim from the original tool so behavior is identical;
levels are grouped and given search text for the new UI.
"""

from __future__ import annotations

from dataclasses import dataclass, field

WOLVERINE_WARNING = (
    "This level needs Wolverine. Go to the Hub first and choose Wolverine before "
    "loading it. Once the level loads you can switch characters."
)


@dataclass(frozen=True)
class Level:
    name: str          # friendly display name
    command: str       # exact console command, e.g. "open Marketplace"
    category: str      # section header in the UI
    subtitle: str = "" # short descriptive line
    warning: str = ""  # confirmation text shown before loading, if any
    aliases: tuple[str, ...] = field(default_factory=tuple)  # extra search terms

    @property
    def search_text(self) -> str:
        return " ".join((self.name, self.subtitle, self.command, *self.aliases)).lower()


LEVELS: list[Level] = [
    # --- Hub & story levels -------------------------------------------------
    Level("Game Menu", "open menu", "Hub & Story", "Title screen, leads to the hub"),
    Level("Ops — Hub", "open Ops", "Hub & Story", "Main hub / mission select"),
    Level("Stark Tower", "open StarkTower", "Hub & Story",
          "Tutorial intro sequence", aliases=("intro", "captain america", "black widow")),
    Level("Hangar", "open Hangar", "Hub & Story", "X-Mansion Hangar", aliases=("x-men", "xmen")),
    Level("Marketplace", "open Marketplace", "Hub & Story",
          "Knowhere Marketplace", aliases=("knowhere",)),
    Level("Throne Room", "open ThroneRoom", "Hub & Story", "Asgard", aliases=("asgard", "thor")),
    Level("Jotunheim", "open Jotunheim", "Hub & Story", "Frost Giant world"),
    Level("Research Lab", "open ResearchLab", "Hub & Story", "Wakanda", aliases=("wakanda", "black panther")),
    Level("Forest", "open Forest", "Hub & Story", "Halfworld", aliases=("halfworld", "rocket")),
    Level("Arena", "open Arena", "Hub & Story", "Sakaar Arena", aliases=("sakaar", "hulk")),
    Level("Downtown", "open DownTown", "Hub & Story", "Downtown New York", aliases=("new york", "nyc")),
    Level("Void", "open Void", "Hub & Story", "Dark Dimension", aliases=("dark dimension", "doctor strange")),
    Level("Palace", "open Palace", "Hub & Story", "Attilan", aliases=("attilan", "inhumans")),
    Level("Sanctuary II", "open SanctuaryII", "Hub & Story",
          "Thanos boss battle", aliases=("thanos", "boss", "final")),

    # --- Special / requires a specific hero ---------------------------------
    Level("Danger Room", "open DangerRoom03", "Special (needs Wolverine)",
          "Room for Training", warning=WOLVERINE_WARNING, aliases=("training", "wolverine")),
    Level("Nick Test Arena", "open Nick_TestArena", "Special (needs Wolverine)",
          "Early Danger Room training map", warning=WOLVERINE_WARNING,
          aliases=("nick", "wolverine", "test")),

    # --- Development / debug -------------------------------------------------
    Level("Move Tutorial", "open MoveTutorial", "Development / Debug",
          "Early movement tutorial (dead ends)", aliases=("moving", "tutorial")),
]


def categories() -> list[str]:
    """Category names in first-seen order."""
    seen: list[str] = []
    for level in LEVELS:
        if level.category not in seen:
            seen.append(level.category)
    return seen


def levels_in(category: str) -> list[Level]:
    return [lvl for lvl in LEVELS if lvl.category == category]
