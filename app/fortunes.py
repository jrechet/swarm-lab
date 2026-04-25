"""Fortune dataset + lookup helpers."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Fortune:
    id: int
    text: str
    author: str = ""


_DATA: tuple[Fortune, ...] = (
    Fortune(1, "Premature optimization is the root of all evil.", "Donald Knuth"),
    Fortune(2, "Simplicity is prerequisite for reliability.", "Edsger Dijkstra"),
    Fortune(3, "Talk is cheap. Show me the code.", "Linus Torvalds"),
    Fortune(4, "Make it work, make it right, make it fast.", "Kent Beck"),
    Fortune(5, "The best way to predict the future is to invent it.", "Alan Kay"),
)


def all_fortunes() -> list[Fortune]:
    return list(_DATA)


def fortune_by_id(fid: int) -> Fortune | None:
    for f in _DATA:
        if f.id == fid:
            return f
    return None
