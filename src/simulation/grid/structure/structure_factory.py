from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Type

from src.simulation.grid.structure.store.barn import Barn
from src.simulation.grid.structure.store.home import Home
from src.simulation.grid.structure.structure import Structure
from src.simulation.grid.structure.structure_type import StructureType
from src.simulation.grid.structure.work.construction.construction_barn import (
    ConstructionBarn,
)
from src.simulation.grid.structure.work.construction.construction_farm import (
    ConstructionFarm,
)
from src.simulation.grid.structure.work.construction.construction_home import (
    ConstructionHome,
)
from src.simulation.grid.structure.work.construction.construction_mine import (
    ConstructionMine,
)
from src.simulation.grid.structure.work.farm import Farm
from src.simulation.grid.structure.work.mine import Mine
from src.simulation.grid.structure.work.tree import Tree

if TYPE_CHECKING:
    from src.simulation.grid.grid import Grid
    from src.simulation.grid.location import Location


class StructureFactory:
    _constructors: Dict[StructureType, Type] = {
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

    def create_instance(
        self, building_type: StructureType, location: Location
    ) -> Structure:
        building_class: Type = self._constructors[building_type]
        return building_class(self._grid, location)
