from abc import ABC

from src.simulation.grid.grid import Grid


class Building(ABC):
    def __init__(
        self,
        grid: Grid,
        x: int,
        y: int,
        width: int,
        height: int,
        construction_char: str,
        char: str,
    ) -> None:
        self._grid: Grid = grid
        self._x: int = x
        self._y: int = y
        self._width: int = width
        self._height: int = height
        self._construction_char: str = construction_char
        self._char: str = char
        # todo add resources or somethin' ie. wood obtained vs wood required, etc.
        self._start_construction()

    def _start_construction(self) -> None:
        # TODO place construction building on the grid, make sure we aren't overlapping with anything else
        pass
