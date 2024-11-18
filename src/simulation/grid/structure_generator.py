from __future__ import annotations

import random
from typing import TYPE_CHECKING, Dict, List, Tuple, Callable

import numpy as np

from src.settings import settings
from src.simulation.grid.disjoint_set import DisjointSet
from src.simulation.grid.location import Location
from src.simulation.grid.structure.structure_type import StructureType
from src.simulation.grid.structure.work.tree import Tree
from src.logger import logger

if TYPE_CHECKING:
    from src.simulation.grid.grid import Grid
    from src.simulation.grid.structure.structure import Structure
    from src.simulation.grid.structure.structure_factory import StructureFactory


class StructureGenerator:
    def __init__(self, grid: Grid, structure_factory: StructureFactory):
        logger.debug("Initializing StructureGenerator with grid and structure_factory.")
        self._grid = grid
        self._structure_factory = structure_factory

    def find_structures(self) -> Dict[Location, Structure]:
        logger.debug("Finding structures in the grid.")
        structures: Dict[Location, Structure] = {}

        for y in range(self._grid.get_height()):
            for x in range(self._grid.get_width()):
                location: Location = Location(x, y)

                if self._grid.is_empty(location):
                    logger.debug(f"Location {location} is empty. Skipping.")
                    continue

                logger.debug(f"Processing location {location}.")

                # Determine the structure type
                if self._grid.is_tree(location):
                    structure_type = StructureType.TREE
                elif self._grid.is_barn(location):
                    structure_type = StructureType.BARN
                elif self._grid.is_home(location):
                    structure_type = StructureType.HOME
                elif self._grid.is_mine(location):
                    structure_type = StructureType.MINE
                elif self._grid.is_farm(location):
                    structure_type = StructureType.FARM
                elif self._grid.is_construction_barn(location):
                    structure_type = StructureType.CONSTRUCTION_BARN
                elif self._grid.is_construction_farm(location):
                    structure_type = StructureType.CONSTRUCTION_FARM
                elif self._grid.is_construction_home(location):
                    structure_type = StructureType.CONSTRUCTION_HOME
                elif self._grid.is_construction_mine(location):
                    structure_type = StructureType.CONSTRUCTION_MINE
                else:
                    logger.error(f"Unknown structure at location {location}.")
                    raise Exception("I see a char you didnt tell me about")

                if structure_type != StructureType.TREE:
                    self._grid.find_top_left_corner(location)

                # Create and store structure
                if location not in structures:
                    logger.debug(f"Creating structure of type {structure_type} at location {location}.")
                    structure = self._structure_factory.create_instance(
                        structure_type, location
                    )
                    if structure:
                        structures[location] = structure
                    else:
                        logger.warning(f"Failed to create structure at location {location}.")

        self._group_tree_yields(list(structures.values()))

        logger.debug(f"Found {len(structures)} structures.")
        return structures

    def _group_tree_yields(self, structures: List[Structure]) -> None:
        logger.debug(f"Grouping trees and generating yields for {len(structures)} structures.")
        trees: List[Tree] = []
        tree_index: Dict[Location, int] = {}
        index: int = 0

        for structure in structures:
            if isinstance(structure, Tree):
                location: Location = structure.get_location()
                tree_index[location] = index
                index += 1
                trees.append(structure)

        logger.debug(f"Found {len(trees)} trees.")

        ds: DisjointSet = DisjointSet(len(trees))
        directions: List[Tuple[int, int]] = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

        for tree in trees:
            location: Location = tree.get_location()
            x, y = location.x, location.y

            for dx, dy in directions:
                nx, ny = x + dx, y + dy

                if 0 <= nx < self._grid.get_height() and 0 <= ny < self._grid.get_width() and self._grid.get_grid()[nx][
                    ny] == settings.get("tree_char", "*"):
                    neighbor_location: Location = Location(nx, ny)
                    if neighbor_location in tree_index:
                        logger.debug(f"Connecting tree at {location} with neighbor {neighbor_location}.")
                        ds.union(tree_index[location], tree_index[neighbor_location])

        grove_groups: Dict[int, List[Tree]] = {}

        for tree in trees:
            location: Location = tree.get_location()
            tree_id: int = tree_index[location]
            root: int = ds.find(tree_id)

            if root not in grove_groups:
                grove_groups[root] = []

            grove_groups[root].append(tree)

        groves: List[List[Tree]] = list(grove_groups.values())

        logger.debug(f"Generated {len(groves)} groves.")
        for grove in groves:
            yield_func: Callable[[], float] = self._generate_random_distribution(10, 50)
            for tree in grove:
                tree.set_yield_func(yield_func)

    @staticmethod
    def _generate_random_distribution(min_val: float, max_val: float) -> Callable[[], float]:
        logger.debug(f"Generating random distribution with min={min_val} and max={max_val}.")
        if min_val >= max_val:
            logger.error("min_val should be less than max_val")
            raise ValueError("min_val should be less than max_val")

        mu: float = random.uniform(min_val, max_val)
        sigma: float = random.uniform(0, (max_val - min_val) / 2)

        return lambda: np.random.normal(mu, sigma)
