from __future__ import annotations

import random
from copy import deepcopy
from typing import TYPE_CHECKING, Dict, List, Optional, Type
from src.settings import settings

from src.simulation.grid.structure_generator import StructureGenerator
from src.simulation.grid.temperature import get_temperature_for_day
from src.simulation.grid.structure.structure import Structure
from src.simulation.grid.grid_generator import GridGenerator
from src.simulation.grid.location import Location
from src.logger import logger

from src.simulation.grid.structure.structure_factory import StructureFactory
from src.simulation.grid.structure.structure_type import StructureType
from src.simulation.grid.grid_disaster_generator import GridDisasterGenerator

if TYPE_CHECKING:
    from src.simulation.simulation import Simulation
    from src.simulation.grid.structure.store.barn import Barn
    from src.simulation.grid.structure.store.home import Home
    from src.simulation.grid.structure.work.farm import Farm
    from src.simulation.grid.structure.work.mine import Mine
    from src.simulation.grid.structure.work.tree import Tree
    from src.simulation.grid.structure.work.work import Work

class Grid:
    def __init__(self, simulation: Simulation, size: int) -> None:
        logger.debug(f"Initializing simulation with grid size {size}.")

        self._simulation: Simulation = simulation
        self._width: int = size
        self._height: int = size

        grid_generator: GridGenerator = GridGenerator(size)
        logger.debug("Generating grid using GridGenerator.")
        self._grid: List[List[str]] = grid_generator.generate()

        self._disaster_generator: GridDisasterGenerator = GridDisasterGenerator(self)
        logger.debug("Initialized disaster generator.")

        self._structure_factory: StructureFactory = StructureFactory(self)
        logger.debug("Initialized structure factory.")

        structure_generator: StructureGenerator = StructureGenerator(self, self._structure_factory)
        logger.debug("Generating structures using StructureGenerator.")
        self._structures: Dict[
            Location, Structure] = structure_generator.find_structures()  # stores the top left corner of every structure

        self._day: int = 0
        self._temp: float = 0
        logger.debug(f"Simulation initialized with {len(self._structures)} structures.")

    def get_time(self) -> int:
        logger.debug("Retrieving simulation time.")
        time = self._simulation.get_time()
        logger.debug(f"Simulation time: {time}")
        return time

    def get_temperature_for_day(self) -> float:
        logger.debug(f"Retrieving temperature for day {self._day}.")
        other_day = self._simulation.get_day()
        if other_day != self._day:
            logger.debug(f"Day has changed from {self._day} to {other_day}. Updating temperature.")
            self._day = other_day
            self._temp = get_temperature_for_day(self._day)
        else:
            logger.debug(f"Temperature for day {self._day} already calculated: {self._temp}.")
        return self._temp

    def generate_disasters(self, chance: float = settings.get("disaster_chance", 0.50)) -> None:
        logger.debug(f"Generating disasters with a chance of {chance}.")
        self._disaster_generator.generate(chance)
        logger.info(f"Disasters generated with a chance of {chance}.")

    def get_grid(self) -> List[List[str]]:
        logger.debug("Retrieving the grid.")
        return self._grid

    def get_buildings(self) -> Dict[Location, Structure]:
        logger.debug("Retrieving buildings (excluding trees).")
        buildings = {
            location: structure
            for location, structure in self._structures.items()
            if not isinstance(structure, Tree)
        }
        logger.debug(f"Found {len(buildings)} buildings.")
        return buildings

    def get_structure(self, location: Location) -> Structure:
        logger.debug(f"Retrieving structure at location {location}.")
        structure = self._structures.get(location)
        if structure:
            logger.debug(f"Structure at {location} found: {structure}.")
        else:
            logger.warning(f"Structure at {location} not found.")
        return structure

    def get_structure_locations(self, structure_type: Type[Structure]) -> List[Location]:
        logger.debug(f"Retrieving locations of structures of type {structure_type}.")
        locations = [
            location
            for location, building in self._structures.items()
            if isinstance(building, structure_type)
        ]
        logger.debug(f"Found {len(locations)} locations for {structure_type}.")
        return locations

    def get_structures(self, structure_type: Type[Structure]) -> List[Structure]:
        logger.debug(f"Retrieving structures of type {structure_type}.")
        locations = self.get_structure_locations(structure_type)
        structures = [self.get_structure(location) for location in locations]
        logger.debug(f"Found {len(structures)} structures of type {structure_type}.")
        return structures

    def get_structure_count(self, structure_type: Type[Structure]) -> int:
        logger.debug(f"Counting structures of type {structure_type}.")
        count = sum(
            1 for structure in self._structures.values() if isinstance(structure, structure_type)
        )
        logger.debug(f"Found {count} structures of type {structure_type}.")
        return count

    def find_top_left_corner(self, where: Location) -> None:
        logger.debug(f"Finding top-left corner starting from {where}.")

        while not self.is_empty(where):
            where.x -= 1
            logger.debug(f"Moved left to {where}.")
        where.x += 1
        logger.debug(f"Adjusted x-coordinate to {where.x}.")

        while not self.is_empty(where):
            where.y -= 1
            logger.debug(f"Moved up to {where}.")
        where.y += 1
        logger.debug(f"Adjusted y-coordinate to {where.y}. Top-left corner found at {where}.")

    def remove(self, structure: Structure, deconstruct: bool = False) -> None:
        logger.debug(f"Removing structure at {structure.get_location()}. Deconstruct: {deconstruct}")

        location = structure.get_location()

        if location in self._structures:
            logger.debug(f"Structure at {location} found. Removing.")
            del self._structures[location]
        else:
            logger.warning(f"Structure at {location} not found in structures.")

        if isinstance(structure, Home):
            logger.debug(f"Removing owner from home at {location}.")
            structure.remove_owner()

        logger.debug(f"Calling remove method on structure at {location}.")
        structure.remove()

        # Ensure the structure is removed once more, just in case
        if location in self._structures:
            logger.debug(f"Structure at {location} found again. Removing.")
            del self._structures[location]

        if deconstruct:
            logger.debug(f"Deconstructing structure at {location}.")
            self._deconstruct_building(structure)

    def _deconstruct_building(self, building: Structure) -> None:
        logger.debug(f"Deconstructing building at {building.get_location()}.")

        if isinstance(building, Home):
            structure_type = StructureType.HOME
            logger.debug(f"Building is a Home. Setting structure type to {structure_type}.")
        elif isinstance(building, Mine):
            structure_type = StructureType.MINE
            logger.debug(f"Building is a Mine. Setting structure type to {structure_type}.")
        elif isinstance(building, Farm):
            structure_type = StructureType.FARM
            logger.debug(f"Building is a Farm. Setting structure type to {structure_type}.")
        elif isinstance(building, Barn):
            structure_type = StructureType.BARN
            logger.debug(f"Building is a Barn. Setting structure type to {structure_type}.")
        else:
            logger.warning(f"Unknown building type {building} for deconstruction. Aborting.")
            return

        structure: Structure = self._structure_factory.create_instance(structure_type, building.get_location())
        logger.debug(f"New {structure_type} structure created at {building.get_location()}.")
        self._structures[structure.get_location()] = structure

    def get_empty_spots_near_town(self) -> List[Location]:
        logger.debug("Starting search for empty spots near towns.")

        rows = len(self._grid)
        cols = len(self._grid[0])
        empty_spots = []
        building_types = "".join([
            settings.get("home_construction_char", "h"),
            settings.get("home_char", "H"),
            settings.get("barn_construction_char", "b"),
            settings.get("barn_char", "B"),
            settings.get("farm_construction_char", "f"),
            settings.get("farm_char", "F"),
            settings.get("mine_construction_char", "m"),
            settings.get("mine_char", "M"),
        ])

        logger.debug(f"Building types to check for: {building_types}")

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

        for i in range(rows):
            for j in range(cols):
                if self._grid[i][j] not in building_types:
                    continue

                location: Location = Location(j, i)
                logger.debug(f"Building or construction found at {location}. Checking surrounding spots.")

                for dx, dy in directions:
                    ni, nj = i + dx, j + dy
                    neighbor_location = Location(nj, ni)

                    if not self.is_in_bounds(neighbor_location):
                        continue
                    if not self.is_empty(neighbor_location):
                        continue

                    logger.debug(f"Empty spot found at {neighbor_location}. Checking adjacency to trees.")

                    # Now check if this empty spot is adjacent to a tree
                    is_adjacent_to_tree = False
                    for ddx, ddy in directions:
                        nn_i, nn_j = ni + ddx, nj + ddy
                        tree_neighbor: Location = Location(nn_j, nn_i)
                        if 0 <= nn_i < rows and 0 <= nn_j < cols and self.is_tree(tree_neighbor):
                            is_adjacent_to_tree = True
                            logger.debug(f"Spot {neighbor_location} is adjacent to tree at {tree_neighbor}.")
                            break

                    if not is_adjacent_to_tree:
                        logger.debug(f"Spot {neighbor_location} is valid and added to empty spots.")
                        empty_spots.append(neighbor_location)

        logger.debug(f"Found {len(empty_spots)} empty spots near towns.")
        return empty_spots

    def grow_trees(self, chance: int = 0.10) -> None:
        logger.debug(f"Starting tree growth process with a chance of {chance}.")

        for i in range(len(self._grid)):
            for j in range(len(self._grid[i])):
                location: Location = Location(j, i)
                tree: Structure = self._structures.get(location)

                if not isinstance(tree, Tree):
                    continue

                logger.debug(f"Tree found at {location}. Checking its neighbors for growth.")

                neighbors: List[Location] = location.get_neighbors()
                random.shuffle(neighbors)

                for neighbor in neighbors:
                    if not self.is_in_bounds(neighbor):
                        logger.debug(f"Neighbor {neighbor} is out of bounds. Skipping.")
                        continue
                    if not self.is_empty(neighbor):
                        logger.debug(f"Neighbor {neighbor} is not empty. Skipping.")
                        continue
                    if random.random() < chance:
                        logger.info(f"Growing tree at {neighbor}.")
                        self._grid[neighbor.y][neighbor.x] = settings.get("tree_char", "*")  # Place a tree here
                        neighbor_tree: Structure = self._structure_factory.create_instance(StructureType.TREE, neighbor)
                        if isinstance(neighbor_tree, Tree):
                            neighbor_tree.set_yield_func(tree.get_yield_func())
                            self._structures[neighbor] = neighbor_tree
                            logger.debug(f"Tree successfully grown at {neighbor}.")
                            break
                        else:
                            logger.debug(f"Failed to create a valid tree structure at {neighbor}.")

        logger.debug("Tree growth process completed.")

    def work_structures_exchange_memories(self):
        logger.debug("Starting memory exchange for work structures.")

        work_structures: List[Work] = list(
            filter(lambda b: not isinstance(b, Work), self._structures.values())
        )

        for work_structure in work_structures:
            logger.debug(f"Exchanging memories for work structure {work_structure}.")
            work_structure.exchange_worker_memories()

        logger.debug("Memory exchange for work structures completed.")

    def start_building_construction(
            self, building_type: StructureType, location: Location
    ) -> None:
        try:
            logger.debug(f"Attempting to start construction of {building_type} at {location}.")
            building: Structure = self._structure_factory.create_instance(
                building_type, location
            )
            logger.info(f"Construction started for {building_type} at {location}.")
        except Exception as e:
            logger.error(f"Could not start structure construction at {location}. Error: {e}")
            return
        self._structures[location] = building
        logger.debug(f"Structure at {location} added to the list of structures.")

    def turn_completed_constructions_to_buildings(self):
        logger.debug("Turning completed constructions into buildings.")

        locations: List[Location] = list(self._structures.keys())
        for location in locations:
            logger.debug(f"Checking structure at {location}.")

            if self.is_construction_barn(location):
                building_type = StructureType.BARN
                logger.debug(f"Construction at {location} is a barn.")
            elif self.is_construction_farm(location):
                building_type = StructureType.FARM
                logger.debug(f"Construction at {location} is a farm.")
            elif self.is_construction_home(location):
                building_type = StructureType.HOME
                logger.debug(f"Construction at {location} is a home.")
            elif self.is_construction_mine(location):
                building_type = StructureType.MINE
                logger.debug(f"Construction at {location} is a mine.")
            else:
                logger.debug(f"Construction at {location} is not recognized. Skipping.")
                continue

            if self._structures[location].has_capacity():
                logger.debug(f"Structure at {location} still has capacity. Skipping.")
                continue

            logger.info(f"Turning construction at {location} into a building.")
            self._structures[location] = self._structure_factory.create_instance(
                building_type, location
            )
            logger.debug(f"Building at {location} updated to {building_type}.")

    def get_open_spot_next_to_town(self) -> Optional[Location]:
        logger.debug("Searching for an open spot next to a town.")

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for location in self._structures:
            logger.debug(f"Checking neighboring spots of structure at {location}.")

            for dx, dy in directions:
                neighbor = Location(location.x + dx, location.y + dy)

                if self.is_in_bounds(neighbor):
                    logger.debug(f"Neighbor {neighbor} is within bounds.")

                    if self.is_empty(neighbor):
                        logger.debug(f"Found open spot at {neighbor}.")
                        return neighbor
                    else:
                        logger.debug(f"Spot at {neighbor} is not empty.")
                else:
                    logger.debug(f"Neighbor {neighbor} is out of bounds.")

        logger.debug("No open spot found next to any town.")
        return None

    def is_in_bounds(self, location: Location) -> bool:
        logger.debug(f"Checking if location {location} is within bounds.")
        in_bounds = 0 <= location.x < self._width and 0 <= location.y < self._height
        logger.debug(f"Location {location} is {'within' if in_bounds else 'out of'} bounds.")
        return in_bounds

    def get_path_finding_matrix(self) -> List[List[int]]:
        logger.debug("Generating path finding matrix.")

        char_to_num: Dict[str, int] = {
            settings.get("home_construction_char", "h"):
                settings.get("home_construction_obstacle_rating", 10),
            settings.get("home_char", "H"):
                settings.get("home_obstacle_rating", 0),
            settings.get("barn_construction_char", "b"):
                settings.get("barn_construction_obstacle_rating", 10),
            settings.get("barn_char", "B"):
                settings.get("barn_obstacle_rating", 0),
            settings.get("farm_construction_char", "f"):
                settings.get("farm_construction_obstacle_rating", 3),
            settings.get("farm_char", "F"):
                settings.get("farm_obstacle_rating", 5),
            settings.get("mine_construction_char", "m"):
                settings.get("mine_construction_obstacle_rating", 0),
            settings.get("mine_char", "M"):
                settings.get("mine_obstacle_rating", 0),
            settings.get("empty_char", " "):
                settings.get("empty_obstacle_rating", 1),
            settings.get("tree_char", "*"):
                settings.get("tree_obstacle_rating", 10),
        }

        logger.debug(f"Character to obstacle rating map: {char_to_num}")

        path_finding_matrix: List[List[int | str]] = deepcopy(self._grid)

        logger.debug(
            f"Starting to fill the path finding matrix based on grid size {len(self._grid)}x{len(self._grid[0])}.")

        for i in range(len(self._grid)):
            row = self._grid[i]
            for j in range(len(row)):
                cell = row[j]
                path_finding_matrix[i][j] = char_to_num[cell]
                logger.debug(f"Setting path_finding_matrix[{i}][{j}] = {char_to_num[cell]} (cell: {cell})")

        logger.debug("Path finding matrix generation complete.")

        return path_finding_matrix

    def is_tree(self, location: Location) -> bool:
        logger.debug(f"Checking if location {location} is a tree.")
        return self.is_char(location, settings.get("tree_char", "*"))

    def is_barn(self, location: Location) -> bool:
        logger.debug(f"Checking if location {location} is a barn.")
        return self.is_char(location, settings.get("barn_char", "B"))

    def is_construction_barn(self, location: Location) -> bool:
        logger.debug(f"Checking if location {location} is a construction barn.")
        return self.is_char(location, settings.get("barn_construction_char", "b"))

    def is_home(self, location: Location) -> bool:
        logger.debug(f"Checking if location {location} is a home.")
        return self.is_char(location, settings.get("home_char", "H"))

    def is_construction_home(self, location: Location) -> bool:
        logger.debug(f"Checking if location {location} is a construction home.")
        return self.is_char(location, settings.get("home_construction_char", "h"))

    def is_farm(self, location: Location) -> bool:
        logger.debug(f"Checking if location {location} is a farm.")
        return self.is_char(location, settings.get("farm_char", "F"))

    def is_construction_farm(self, location: Location) -> bool:
        logger.debug(f"Checking if location {location} is a construction farm.")
        return self.is_char(location, settings.get("farm_construction_char", "f"))

    def is_mine(self, location: Location) -> bool:
        logger.debug(f"Checking if location {location} is a mine.")
        return self.is_char(location, settings.get("mine_char", "M"))

    def is_construction_mine(self, location: Location) -> bool:
        logger.debug(f"Checking if location {location} is a construction mine.")
        return self.is_char(location, settings.get("mine_construction_char", "m"))

    def is_empty(self, location: Location) -> bool:
        logger.debug(f"Checking if location {location} is empty.")
        return self.is_char(location, settings.get("empty_char", " "))

    def is_char(self, location: Location, char: str) -> bool:
        logger.debug(f"Checking if location {location} contains character '{char}'.")
        return self._grid[location.y][location.x] == char

    def get_width(self) -> int:
        logger.debug("Getting grid width.")
        return self._width

    def get_height(self) -> int:
        logger.debug("Getting grid height.")
        return self._height

    def flush(self):
        logger.debug("Flushing disaster generator.")
        self._disaster_generator.flush()

    def get_disaster_counts(self) -> Dict[str, int]:
        logger.debug("Getting disaster counts.")
        return self._disaster_generator.get_disaster_counts()
