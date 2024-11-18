from __future__ import annotations

from abc import ABC, abstractmethod

from typing import TYPE_CHECKING

from src.settings import settings
from src.simulation.grid.location import Location
from src.logger import logger  # Assuming you want to log activity

if TYPE_CHECKING:
    from src.simulation.grid.grid import Grid


class Structure(ABC):
    def __init__(
            self,
            grid: Grid,
            location: Location,  # top left corner
            width: int,
            height: int,
            char: str,
    ):
        logger.debug(f"Initializing structure at {location}, size: {width}x{height}, char: {char}")

        self._grid: Grid = grid
        self._location = location
        self._width: int = width
        self._height: int = height
        self._char: str = char
        if not self._grid.is_char(location, char):  # this is important for the first pass on the grid
            self._add_structure_on_grid()

    def _validate_structure_area(self, is_adding: bool) -> None:
        """
        A helper method to validate the area where a structure is being placed or removed.
        This checks if the structure is within bounds and ensures the area is either empty (for adding)
        or already occupied by the structure (for removing).

        :param is_adding: True if adding a structure, False if removing a structure.
        """
        logger.debug(
            f"Validating structure area at {self._location}, size: {self._width}x{self._height}, adding: {is_adding}")

        for dy in range(self._height):
            for dx in range(self._width):
                location = Location(self._location.x + dx, self._location.y + dy)

                # Check if the location is within bounds
                if not self._grid.is_in_bounds(location):
                    raise ValueError(f"Location {location} is out of bounds")

                # Check if adding: location must be empty or contain a tree
                if is_adding:
                    if not self._grid.is_empty(location) and not self._grid.is_tree(location):
                        raise ValueError(f"Location {location} is already occupied by another building or tree")
                # Check if removing: location must be occupied by the structure
                else:
                    if self._grid.get_grid()[location.y][location.x] != self._char:
                        raise ValueError(f"No structure found at {location} to remove")

        logger.debug(f"Validation passed for area at {self._location}")

    def _add_structure_on_grid(self) -> None:
        """
        This method sets up the construction on the grid by verifying the location
        and ensuring no overlap with existing structures or trees.
        Construction can only start once all required resources are delivered.
        """
        logger.debug(f"Adding structure at {self._location}, char: {self._char}")

        if self._char == settings.get("tree_char", "*"):
            return

        # Validate the area before placing the structure
        self._validate_structure_area(is_adding=True)

        # If all checks pass, place the structure on the grid
        for dy in range(self._height):
            for dx in range(self._width):
                location = Location(self._location.x + dx, self._location.y + dy)
                self._grid.get_grid()[location.y][location.x] = self._char

        logger.info(f"Structure added at {self._location}, char: {self._char}")

    def remove(self) -> None:
        logger.debug(f"Removing structure at {self._location}, char: {self._char}")
        self._remove_structure_on_grid()

    def _remove_structure_on_grid(self) -> None:
        """
        This method removes a structure from the grid, clearing the locations
        occupied by the structure. It checks if the structure is present at the
        specified location and only removes it if no other structures are in the way.
        """
        logger.debug(f"Removing structure at {self._location}, char: {self._char}")

        # Validate the area before removing the structure
        self._validate_structure_area(is_adding=False)

        # If all checks pass, proceed to remove the structure
        for dy in range(self._height):
            for dx in range(self._width):
                location = Location(self._location.x + dx, self._location.y + dy)
                # Clear the cell (remove the structure)
                self._grid.get_grid()[location.y][location.x] = settings.get("empty_char", " ")

        logger.info(f"Structure removed at {self._location}, char: {self._char}")

    def get_location(self):
        return self._location

    def get_height(self) -> int:
        return self._height

    def get_width(self) -> int:
        return self._width

    def _get_location(self) -> Location:
        return self._location

    @abstractmethod
    def has_capacity(self) -> bool:
        # Can someone else be in or use the structure
        # Called by the building type.
        pass

    @staticmethod
    @abstractmethod
    def work_time_estimate() -> int:
        # How long will it take to finish work at this structure?
        pass
