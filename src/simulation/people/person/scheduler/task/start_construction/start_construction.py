from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, List, Optional, override

from src.simulation.grid.location import Location
from src.simulation.grid.structure.structure_type import StructureType
from src.simulation.people.person.scheduler.task.task import Task
from src.simulation.people.person.scheduler.task.task_type import TaskType

if TYPE_CHECKING:
    from src.simulation.grid.structure.structure import Structure
    from src.simulation.people.person.person import Person
    from src.simulation.simulation import Simulation


class StartConstruction(Task, ABC):
    def __init__(
        self,
        simulation: Simulation,
        person: Person,
        priority: int,
        width: int,
        height: int,
        building_type: StructureType,
        task_type: TaskType
    ) -> None:
        super().__init__(simulation, person, priority, task_type)
        self._width: int = width + 2
        self._height: int = height + 2
        self._building_type: StructureType = building_type
        self._search_time: int = 0

    @override
    def execute(self) -> None:
        self._search_time += 1
        if self._search_time >= 20:  # todo: I don't wanna put this one in the yaml
            self._finished(False)
            return
        empties: List[Location] = self._person.get_empties()
        location = self._find_fitting_group(empties)
        if location:
            if self._person.get_location().is_one_away(location):
                self._simulation.get_grid().start_building_construction(self._building_type, location)
                self._finished()
            else:
                self._person.go_to_location(location)
        else:
            self._person.go_to_location(self._get_closest_edge_of_town())

    def _get_closest_edge_of_town(self) -> Location:
        # Get the current location of the person
        current_location: Location = self._person.get_location()

        # Get the list of locations occupied by buildings
        building_locations: List[Location] = self._person.get_buildings()

        # Calculate the bounding box of the building locations
        min_x = min(building_loc.x for building_loc in building_locations)
        max_x = max(building_loc.x for building_loc in building_locations)
        min_y = min(building_loc.y for building_loc in building_locations)
        max_y = max(building_loc.y for building_loc in building_locations)

        # Define the four corners of the bounding box
        top_left = Location(min_x, min_y)
        top_right = Location(max_x, min_y)
        bottom_left = Location(min_x, max_y)
        bottom_right = Location(max_x, max_y)

        # List of all the corners
        corners = [top_left, top_right, bottom_left, bottom_right]

        # Find the closest corner by calculating the distance
        closest_corner = min(corners, key=lambda loc: current_location.distance_to(loc))

        return closest_corner

    def _find_fitting_group(self, empties: List[Location]) -> Optional[Location]:
        groups = self._get_groups(empties)

        for group in groups:
            # Get the bounding box of the current group of locations
            min_x = min(loc.x for loc in group)
            max_x = max(loc.x for loc in group)
            min_y = min(loc.y for loc in group)
            max_y = max(loc.y for loc in group)

            group_width = max_x - min_x + 1
            group_height = max_y - min_y + 1

            # Check if the bounding box fits within the given width and height
            # First orientation (width × height)
            if group_width <= self._width and group_height <= self._height:
                return Location(min_x, min_y)
            # Second orientation (height × width), checking if rotated box fits
            elif group_width <= self._height and group_height <= self._width:
                return Location(min_x, min_y)

        return None

    @staticmethod
    def _get_groups(empties: List[Location]) -> List[List[Location]]:
        visited = set()  # Keep track of visited locations
        groups = []  # List of groups, where each group is a list of locations

        def dfs(l: Location, g: List[Location]):
            nonlocal visited
            # Mark the location as visited
            visited.add(l)
            g.append(l)

            # Explore neighbors
            for neighbor in l.get_neighbors():
                if neighbor in empties and neighbor not in visited:
                    dfs(neighbor, g)

        for location in empties:
            if location not in visited:
                group = []
                dfs(location, group)
                groups.append(group)

        return groups

    @override
    def get_remaining_time(self) -> int:
        return 10

    @override
    def _clean_up_task(self) -> None:
        # nothing to do here
        pass

    @override
    def get_work_structure(self) -> Optional[Structure]:
        return None
