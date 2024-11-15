import random
from copy import deepcopy
from typing import Dict, List, Optional, Type

from src.simulation.grid.structure.store.barn import Barn
from src.simulation.grid.structure.store.home import Home
from src.simulation.grid.structure.work.farm import Farm
from src.simulation.grid.structure.work.mine import Mine
from src.simulation.grid.structure.work.tree import Tree
from src.simulation.grid.structure.work.work import Work

from src.simulation.grid.structure_generator import StructureGenerator
from src.simulation.grid.temperature import get_temperature_for_day
from src.simulation.simulation import Simulation
from structure.structure import Structure
from grid_generator import GridGenerator
from location import Location
from src.logger import logger

from src.simulation.grid.structure.structure_factory import StructureFactory
from src.simulation.grid.structure.structure_type import StructureType
from src.simulation.grid.grid_disaster_generator import GridDisasterGenerator

class Grid:
    def __init__(self, simulation: Simulation, size: int) -> None:
        self._simulation: Simulation = simulation
        self._width: int = size
        self._height: int = size
        
        grid_generator: GridGenerator = GridGenerator(size)
        self._grid: List[List[str]] = grid_generator.generate()
        
        self._disaster_generator = GridDisasterGenerator(self)

        self._structure_factory = StructureFactory(self)
        structure_generator: StructureGenerator = StructureGenerator(self, self._structure_factory)
        self._structures: Dict[Location, Structure] = structure_generator.find_structures() # stores the top left corner of every structure

        self._day: int = 0
        self._temp: float = 0

    def get_time(self) -> int:
        return self._simulation.get_time()

    def get_temperature_for_day(self) -> float:
        other_day = self._simulation.get_day()
        if other_day != self._day:
            self._day = other_day
            self._temp = get_temperature_for_day(self._day)
        return self._temp

    def generate_disasters(self, chance: float = 0.50) -> None:
        self._disaster_generator.generate(chance)

    def get_grid(self) -> List[List[str]]:
        return self._grid

    def get_buildings(self) -> Dict[Location, Structure]:
        return {location: structure for location, structure in self._structures.items() if not isinstance(structure, Tree)}

    def get_structure(self, location: Location) -> Structure:
        return self._structures[location]

    def get_structure_locations(self, structure_type: Type[Structure]) -> List[Location]:
        # Get the list of locations containing structures of the specified type
        return [
            location
            for location, building in self._structures.items()
            if isinstance(building, structure_type)
        ]

    def get_structures(self, structure_type: Type[Structure]) -> List[Structure]:
        # Use get_structure_locations to get locations of the desired structure type
        locations = self.get_structure_locations(structure_type)
        # Retrieve and return the structures of the specified type
        return [self.get_structure(location) for location in locations]

    def get_structure_count(self, structure_type: Type[Structure]) -> int:
        # Iterate through the values of the _buildings dictionary and count instances of Home
        return sum(
            1 for structure in self._structures.values() if isinstance(structure, structure_type)
        )

    def find_top_left_corner(self, where: Location) -> None:
        while not self.is_empty(where):
            where.x -= 1
        where.x += 1
        while not self.is_empty(where):
            where.y -= 1
        where.y += 1

    def remove(self, structure: Structure, deconstruct: bool = False) -> None:
        del self._structures[structure.get_location()]
        if isinstance(structure, Home):
            structure.remove_owner()
        structure.remove()
        del self._structures[structure.get_location()]
        if deconstruct:
            self._deconstruct_building(structure)

    def _deconstruct_building(self, building: Structure) -> None:
        if isinstance(building, Home):
            structure_type: StructureType = StructureType.HOME
        elif isinstance(building, Mine):
            structure_type: StructureType = StructureType.MINE
        elif isinstance(building, Farm):
            structure_type: StructureType = StructureType.FARM
        elif isinstance(building, Barn):
            structure_type: StructureType = StructureType.BARN
        else:
            return
        structure: Structure = self._structure_factory.create_instance(structure_type, building.get_location())
        self._structures[structure.get_location()] = structure

    def get_empty_spots_near_town(self) -> List[Location]:
        rows = len(self._grid)
        cols = len(self._grid[0])
        empty_spots = []

        # List of possible directions: (up, down, left, right, and 4 diagonal directions)
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

        for i in range(rows):
            for j in range(cols):
                # Check if the current cell is a building (or under construction)
                if self._grid[i][j] in "MFHBFmhfb":
                    # Check all 8 directions around the current building location
                    for dx, dy in directions:
                        ni, nj = i + dx, j + dy
                        # Ensure the new position is within bounds
                        if 0 <= ni < rows and 0 <= nj < cols:
                            # If it's an empty space, we add it as a candidate
                            if self._grid[ni][nj] == " ":
                                # Now, check if this empty space is adjacent to a tree ('*')
                                is_adjacent_to_tree = False
                                for ddx, ddy in directions:
                                    nn_i, nn_j = ni + ddx, nj + ddy
                                    if 0 <= nn_i < rows and 0 <= nn_j < cols and self._grid[nn_i][nn_j] == "*":
                                        is_adjacent_to_tree = True
                                        break

                                # Add the empty space if it's not adjacent to a tree
                                if not is_adjacent_to_tree:
                                    empty_spots.append(Location(ni, nj))

        return empty_spots

    def grow_trees(self, chance: int = 0.10) -> None:
        for i in range(len(self._grid)):
            for j in range(len(self._grid[i])):
                location: Location = Location(i, j)
                tree: Structure = self._structures[location]
                if not isinstance(tree, Tree):
                    continue
                neighbors: List[Location] = location.get_neighbors()
                random.shuffle(neighbors)
                for neighbor in neighbors:
                    if not self.is_location_in_bounds(neighbor) or not self.is_empty(neighbor):
                        continue
                    if random.random() < chance:
                        self._grid[neighbor.y][neighbor.x] = "*"  # Place a tree here
                        neighbor_tree: Structure = self._structure_factory.create_instance(StructureType.TREE, neighbor)
                        if isinstance(neighbor_tree, Tree):
                            neighbor_tree.set_yield_func(tree.get_yield_func())
                            self._structures[neighbor] = neighbor_tree
                            break

    def work_structures_exchange_memories(self):
        work_structures: List[Work] = list(
            filter(lambda b: not isinstance(b, Work), self._structures.values())
        )
        for work_structure in work_structures:
            work_structure.exchange_worker_memories()

    def start_building_construction(
        self, building_type: StructureType, location: Location
    ) -> None:
        try:
            building: Structure = self._structure_factory.create_instance(
                building_type, location
            )
        except Exception as e:
            logger.error("Could not start structure construction", e)
            return
        self._structures[location] = building

    def turn_completed_constructions_to_buildings(self):
        locations: List[Location] = list(self._structures.keys())
        for location in locations:
            if self.is_construction_barn(location):
                building_type = StructureType.BARN
            elif self.is_construction_farm(location):
                building_type = StructureType.FARM
            elif self.is_construction_home(location):
                building_type = StructureType.HOME
            elif self.is_construction_mine(location):
                building_type = StructureType.MINE
            else:
                continue
            if self._structures[location].has_capacity():
                continue
            self._structures[location] = self._structure_factory.create_instance(
                building_type, location
            )

    def get_open_spot_next_to_town(self) -> Optional[Location]:
        # List of possible directions to check (up, down, left, right)
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        # Iterate over all the buildings
        for location in self._structures:
            # Check all adjacent locations
            for dx, dy in directions:
                neighbor = Location(location.x + dx, location.y + dy)

                # Check if the neighbor is within bounds and is empty
                if self.is_location_in_bounds(neighbor) and self.is_empty(neighbor):
                    return neighbor

        # If no open spot was found, return None
        return None

    def is_valid_location_for_person(self, location: Location) -> bool:
        return self.is_empty(location)

    def is_location_in_bounds(self, location: Location) -> bool:
        return 0 <= location.x < self._width and 0 <= location.y < self._height

    def get_path_finding_matrix(self) -> List[List[int]]:
        char_to_num: Dict[str, int] = {
            "h": 10,
            "H": 0,
            "b": 10,
            "B": 0,
            "f": 3,
            "F": 5,
            "m": 0,
            "M": 0,
            " ": 1,
            "*": 10,
        }
        path_finding_matrix: List[List[int | str]] = deepcopy(self._grid)
        for i in range(len(self._grid)):
            row = self._grid[i]
            for j in range(len(row)):
                cell = row[j]
                path_finding_matrix[i][j] = char_to_num[cell]
        return path_finding_matrix

    def is_tree(self, location: Location) -> bool:
        return self._is_item(location, "*")

    def is_barn(self, location: Location) -> bool:
        return self._is_item(location, "B")

    def is_construction_barn(self, location: Location) -> bool:
        return self._is_item(location, "b")

    def is_home(self, location: Location) -> bool:
        return self._is_item(location, "H")

    def is_construction_home(self, location: Location) -> bool:
        return self._is_item(location, "h")

    def is_farm(self, location: Location) -> bool:
        return self._is_item(location, "F")

    def is_construction_farm(self, location: Location) -> bool:
        return self._is_item(location, "f")

    def is_mine(self, location: Location) -> bool:
        return self._is_item(location, "M")

    def is_construction_mine(self, location: Location) -> bool:
        return self._is_item(location, "m")

    def is_empty(self, location: Location) -> bool:
        return self._is_item(location, " ")

    def _is_item(self, location: Location, char: str) -> bool:
        return self._grid[location.y][location.x] == char

    def get_width(self) -> int:
        return self._width

    def get_height(self) -> int:
        return self._height

    def flush(self):
        self._disaster_generator.flush()

    def get_disaster_counts(self) -> Dict[str, int]:
        return self._disaster_generator.get_disaster_counts()
