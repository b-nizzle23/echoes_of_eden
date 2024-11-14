from typing import override

from src.simulation.grid.grid import Grid
from src.simulation.grid.structure.store.barn import Barn
from src.simulation.grid.structure.store.home import Home
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
from src.simulation.visualization.state.state import State


class GridState(State):
    @override
    def __init__(self, grid: Grid):
        self._barn_count: int = grid.get_structure_count(Barn)
        self._construction_barn_count: int = grid.get_structure_count(ConstructionBarn)
        self._farm_count: int = grid.get_structure_count(Farm)
        self._construction_farm_count: int = grid.get_structure_count(ConstructionFarm)
        self._mine_count: int = grid.get_structure_count(Mine)
        self._construction_mine_count: int = grid.get_structure_count(ConstructionMine)
        self._home_count: int = grid.get_structure_count(Home)
        self._construction_home_count: int = grid.get_structure_count(ConstructionHome)
        self._tree_count: int = grid.get_structure_count(Tree)

