import random
from typing import Dict, List, Tuple, Callable

import numpy as np

from src.simulation.grid.disjoint_set import DisjointSet
from src.simulation.grid.grid import Grid
from src.simulation.grid.location import Location
from src.simulation.grid.structure.structure import Structure
from src.simulation.grid.structure.structure_factory import StructureFactory
from src.simulation.grid.structure.structure_type import StructureType
from src.simulation.grid.structure.work.tree import Tree


class StructureGenerator:
    def __init__(self, grid: Grid, structure_factory: StructureFactory):
        self._grid = grid
        self._structure_factory = structure_factory

    def find_structures(self) -> Dict[Location, Structure]:
        structures: Dict[Location, Structure] = {}
        # Iterate over the grid and check each location
        for y in range(self._grid.get_height()):
            for x in range(self._grid.get_width()):
                location: Location = Location(x, y)
    
                # Skip empty spaces or trees
                if self._grid.is_empty(location):
                    continue
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
                    raise Exception("I see a char you didnt tell me about")
    
                # Create a new structure instance and associate it with the first location
                # (we could use the top-left corner as the "representative" location for each structure)
                if location not in structures:
                    structure = self._structure_factory.create_instance(
                        structure_type, location
                    )
                    if not structure:
                        continue
                    # TODO make sure we only have the top left location for each structure in the dictionary
                    structures[location] = structure
        self._group_tree_yields(list(structures.values()))
        return structures
        
    def _group_tree_yields(self, structures: List[Structure]) -> None:
        trees: List[Tree] = []
        for structure in structures:
            if isinstance(structure, Tree):
                trees.append(structure)
    
        # Create a map from tree location to an index in the disjoint set
        tree_index: Dict[Location, int] = {}
        index: int = 0
    
        for tree in trees:
            location: Location = tree.get_location()
            tree_index[location] = index
            index += 1
    
        # Create a disjoint set for the number of trees
        ds: DisjointSet = DisjointSet(len(trees))
    
        # Directions for neighbors: up, down, left, right, and diagonals
        directions: List[Tuple[int, int]] = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    
        # Traverse the grid and connect trees if they are neighbors
        for tree in trees:
            location: Location = tree.get_location()
            x, y = location.x, location.y
    
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
    
                # Check if the new location is within bounds and contains a tree
                if 0 <= nx < self._grid.get_height() and 0 <= ny < self._grid.get_width() and self._grid.get_grid()[nx][ny] == "*":
                    neighbor_location: Location = Location(nx, ny)
                    if neighbor_location in tree_index:
                        # Union the current tree with its neighboring tree
                        ds.union(tree_index[location], tree_index[neighbor_location])
    
        # Now that we have connected the trees, group them by their root parent
        grove_groups: Dict[int, List[Tree]] = {}
    
        for tree in trees:
            location: Location = tree.get_location()
            tree_id: int = tree_index[location]
            root: int = ds.find(tree_id)
    
            if root not in grove_groups:
                grove_groups[root] = []
    
            grove_groups[root].append(tree)
    
        # At this point, grove_groups contains the groups of connected trees
        # Each group (grove) is a list of Tree objects
        groves: List[List[Tree]] = list(grove_groups.values())
    
        for grove in groves:
            yield_func: Callable[[], float] = self._generate_random_distribution(10, 50)
            for tree in grove:
                tree.set_yield_func(yield_func)
    
    @staticmethod
    def _generate_random_distribution(min_val: float, max_val: float) -> Callable[[], float]:
        # Ensure the min is smaller than the max
        if min_val >= max_val:
            raise ValueError("min_val should be less than max_val")
    
        # Generate random mean (mu) within the range [min_val, max_val]
        mu: float = random.uniform(min_val, max_val)
    
        # Generate random standard deviation (sigma), ensuring it is reasonable
        sigma: float = random.uniform(0, (max_val - min_val) / 2)
    
        # Return a lambda function that generates a random sample from a normal distribution
        return lambda: np.random.normal(mu, sigma)
