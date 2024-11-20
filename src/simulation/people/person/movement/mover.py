from __future__ import annotations

from copy import deepcopy
from random import randint
from typing import TYPE_CHECKING, List, Optional

from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid as PathFindingGrid
from pathfinding.core.node import GridNode as PathFindingGridNode
from pathfinding.finder.a_star import AStarFinder

from src.settings import settings
from src.simulation.grid.location import Location
from src.simulation.people.person.movement.vision import Vision

if TYPE_CHECKING:
    from src.simulation.grid.grid import Grid
    from src.simulation.people.person.memories import Memories
    from src.simulation.people.person.person import Person
    from src.logger import logger


class Mover:
    def __init__(self, grid: Grid, person: Person, memories: Memories, speed: int) -> None:
        logger.info(f"Initializing Mover for person {person} with speed {speed}.")
        self._person = person
        self._grid = grid
        self._speed = speed
        self._memories = memories
        self._vision = Vision(person, grid, settings.get("visibility", 15))
        self._path_finding_grid = self._get_path_finding_grid()
        logger.debug("Mover initialized with grid: %s, person: %s, speed: %d.", grid, person, speed)

    def explore(self) -> None:
        logger.info("Explorer is searching for a random location.")
        random_location = self._get_random_location()
        logger.debug(f"Random location chosen: {random_location}")
        self.towards(random_location)

    def towards(self, target: Location) -> None:
        logger.info(f"Moving towards target location: {target}.")
        if not self._grid.is_in_bounds(target):
            logger.warning(f"Target location {target} is out of bounds, aborting movement.")
            return

        if self._invalid(target):
            logger.debug(f"Target location {target} is invalid, adjusting target.")
            target = self._adjust_target(target)

        vision = Vision(self._person, self._grid, settings.get("visibility", 10))

        for _ in range(self._speed):
            logger.debug(f"Step {_}: Combining vision with current memories.")
            self._memories.combine(vision.look_around())
            path = self._get_path(target)

            if path and len(path) >= 2:
                next_node = path[1]
                new_location = Location(next_node.y, next_node.x)  # Convert to Location
                logger.debug(f"Moving to next location: {new_location}.")
                self._place(new_location)
            else:
                logger.warning(f"No valid path found to target: {target}")

    def _invalid(self, location: Location) -> bool:
        logger.info(f"Checking if location {location} is invalid (barn, mine, or home).")
        result = self._grid.is_barn(location) or self._grid.is_mine(location) or self._grid.is_home(location)
        logger.debug(f"Location {location} is invalid: {result}")
        return result

    def _adjust_target(self, target):
        logger.info(f"Adjusting target location {target} if necessary.")
        neighbors: List[Location] = target.get_neighbors()
        found: bool = False
        for neighbor in neighbors:
            logger.debug(f"Checking if neighbor location {neighbor} is valid.")

            if not self._invalid(neighbor) and self.can_get_to(neighbor):
                target = neighbor
                found = True
                logger.debug("New valid target found: {target}")
                break
        if not found:
            logger.error("No valid targets found for movement. Raising exception.")
            raise Exception("Can only move to empty spaces.")
        return target

    def get_closest(self, locations: List[Location], current_location=None) -> Optional[Location]:
        logger.info(f"Getting the closest location from {current_location} to one of the target locations.")
        if not current_location:
            current_location = self._person.get_location()
            logger.debug(f"Current location not provided. Using person's current location: {current_location}")
        if not locations:
            logger.warning("No target locations provided. Returning None.")
            return None
        closest_location = min(locations, key=lambda loc: current_location.distance_to(loc), default=None)
        logger.debug(f"Closest location found: {closest_location}")
        return closest_location

    def can_get_to(self, target: Location) -> bool:
        logger.debug(f"Checking if a path exists to target location {target}")
        path_exists = bool(self._get_path(target))
        logger.debug(f"Path to target {target} exists: {path_exists}")
        return path_exists

    def _place(self, location: Location) -> None:
        logger.info(f"Placing person at location {location}")
        current_location = deepcopy(self._person.get_location())

        if not current_location.is_one_away(location):
            logger.error(f"Attempted to place person at location {location}, which is not one away from current location {current_location}.")
            raise ValueError(f"Location is not one away: {location}")

        if not self._grid.is_in_bounds(location) or self._invalid(location):
            logger.error(f"Attempted to place person at invalid location {location}")
            raise ValueError(f"Location is not valid: {location} {self._grid.get_grid()[location.y][location.x]}")

        self._person.set_location(location)
        logger.debug(f"Person successfully placed at location {location}")

    def _get_random_location(self) -> Location:
        logger.info("Getting a random valid location.")

        while True:
            x = randint(0, self._grid.get_width() - 1)
            y = randint(0, self._grid.get_height() - 1)
            location = Location(x, y)

            if self._grid.is_in_bounds(location) and not self._invalid(location) and self.can_get_to(location):
                logger.debug(f"Random location found: {location}")
                return location

            logger.debug(f"Generated invalid location {location}. Trying again...")

    def _get_path(
        self,
        target: Location,
    ) -> List[PathFindingGridNode]:
        logger.info(f"Finding path to target location {target}")
        start: Location = deepcopy(self._person.get_location())

        if not self._grid.is_in_bounds(start) or self._invalid(start):
            logger.error(f"Start location {start} is out of bounds or invalid. Raising exception.")
            raise ValueError("Person out of bounds")

        start_node = self._path_finding_grid.node(start.y, start.x)
        end_node = self._path_finding_grid.node(target.y, target.x)

        logger.debug(f"Start node: {start_node}, End node: {end_node}")

        finder = AStarFinder(diagonal_movement=DiagonalMovement.always)

        path, _ = finder.find_path(start_node, end_node, self._path_finding_grid)
        logger.debug(f"Path found: {path}")
        return path

    def _get_path_finding_grid(self) -> PathFindingGrid:
        logger.info("Generating pathfinding grid.")

        # Get the pathfinding matrix from the grid
        matrix = self._grid.get_path_finding_matrix()
        logger.debug(f"Pathfinding matrix retrieved: {matrix}")

        return PathFindingGrid(matrix=matrix)

    # For debugging
    def _print_grid(self, target: Location, path) -> None:
        logger.info("Printing grid.")

        grid = self._grid.get_grid()
        person_location = self._person.get_location()

        # Extract y (row) and x (column) from the Location object for the person
        person_y = person_location.y  # row
        person_x = person_location.x  # column

        # Extract y (row) and x (column) from the Location object for the target
        target_y = target.y  # row
        target_x = target.x  # column

        # Convert path from nodes (e.g., tuples) to Location objects
        path_locations = [Location(y, x) for y, x in path]

        # Log the grid dimensions and target position
        logger.debug(f"Grid dimensions: {len(grid)} x {len(grid[0])}")
        logger.debug(f"Target position: ({target_y}, {target_x})")

        # Top border: Adjusted to account for spaces between characters
        border = "+" + "-" * len(grid[0]) + "+"
        print(border)
        logger.debug("Top border printed.")

        # Print each row with characters joined by an empty string
        for y_idx, row in enumerate(grid):
            row_display = []
            for x_idx, cell in enumerate(row):
                # If we're at the person's location, mark it with 'P'
                if y_idx == person_y and x_idx == person_x:
                    row_display.append("P")
                # If we're at the target's location, mark it with 'T'
                elif y_idx == target_y and x_idx == target_x:
                    row_display.append("T")
                # If we're at a location in the path, mark it with 'r'
                elif Location(y_idx, x_idx) in path_locations:
                    row_display.append("r")
                else:
                    row_display.append(cell)  # otherwise, display the normal grid cell

            # Log each row before printing for debugging purposes
            logger.debug(f"Row {y_idx}: {' '.join(row_display)}")

            # Print the row with no spaces between characters (join with an empty string)
            print("|" + " ".join(row_display) + "|")

        # Bottom border: Same as top border
        print(border)
        logger.debug("Bottom border printed.")
