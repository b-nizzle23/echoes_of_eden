from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Type

import logging

from src.simulation.grid.structure.store.barn import Barn
from src.simulation.grid.structure.store.home import Home
from src.simulation.grid.structure.structure import Structure
from src.simulation.grid.structure.structure_type import StructureType
from src.simulation.grid.structure.work.construction.construction_barn import ConstructionBarn
from src.simulation.grid.structure.work.construction.construction_farm import ConstructionFarm
from src.simulation.grid.structure.work.construction.construction_home import ConstructionHome
from src.simulation.grid.structure.work.construction.construction_mine import ConstructionMine
from src.simulation.grid.structure.work.farm import Farm
from src.simulation.grid.structure.work.mine import Mine
from src.simulation.grid.structure.work.tree import Tree

if TYPE_CHECKING:
    from src.simulation.grid.grid import Grid
    from src.simulation.grid.location import Location

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class StructureFactory:
    _constructors: Dict[StructureType, Type[Structure]] = {
        StructureType.HOME: Home,
        StructureType.BARN: Barn,
        StructureType.MINE: Mine,
        StructureType.FARM: Farm,
        StructureType.TREE: Tree,
        StructureType.CONSTRUCTION_BARN: ConstructionBarn,
        StructureType.CONSTRUCTION_HOME: ConstructionHome,
        StructureType.CONSTRUCTION_FARM: ConstructionFarm,
        StructureType.CONSTRUCTION_MINE: ConstructionMine,
    }

    def __init__(self, grid: Grid) -> None:
        self._grid = grid
        logger.debug(f"StructureFactory initialized with grid: {self._grid}")

    def create_instance(self, building_type: StructureType, location: Location) -> Structure:
        logger.debug(f"Creating structure of type {building_type} at location {location}")

        # Check if building_type is valid
        if building_type not in self._constructors:
            logger.error(f"Invalid structure type: {building_type}")
            raise ValueError(f"Invalid structure type: {building_type}")

        building_class: Type[Structure] = self._constructors[building_type]
        structure = building_class(self._grid, location)

        logger.info(f"Structure of type {building_type} created at location {location}")
        return structure
