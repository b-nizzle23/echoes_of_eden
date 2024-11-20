from typing import override

from src.simulation.grid.grid import Grid
from src.simulation.grid.structure.store.barn import Barn
from src.simulation.grid.structure.store.home import Home
from src.simulation.grid.structure.structure_factory import logger
from src.simulation.grid.structure.work.construction.construction_barn import \
    ConstructionBarn
from src.simulation.grid.structure.work.construction.construction_farm import \
    ConstructionFarm
from src.simulation.grid.structure.work.construction.construction_home import \
    ConstructionHome
from src.simulation.grid.structure.work.construction.construction_mine import \
    ConstructionMine
from src.simulation.grid.structure.work.farm import Farm
from src.simulation.grid.structure.work.mine import Mine
from src.simulation.grid.structure.work.tree import Tree
from src.simulation.visualization.state.state import State


class GridState(State):
    @override
    def __init__(self, grid: Grid):
        self._barn_count: int = grid.get_structure_count(Barn)
        logger.debug(f"Barn count: {self._barn_count}")

        self._construction_barn_count: int = grid.get_structure_count(ConstructionBarn)
        logger.debug(f"Construction barn count: {self._construction_barn_count}")

        self._farm_count: int = grid.get_structure_count(Farm)
        logger.debug(f"Farm count: {self._farm_count}")

        self._construction_farm_count: int = grid.get_structure_count(ConstructionFarm)
        logger.debug(f"Construction farm count: {self._construction_farm_count}")

        self._mine_count: int = grid.get_structure_count(Mine)
        logger.debug(f"Mine count: {self._mine_count}")

        self._construction_mine_count: int = grid.get_structure_count(ConstructionMine)
        logger.debug(f"Construction mine count: {self._construction_mine_count}")

        self._home_count: int = grid.get_structure_count(Home)
        logger.debug(f"Home count: {self._home_count}")

        self._construction_home_count: int = grid.get_structure_count(ConstructionHome)
        logger.debug(f"Construction home count: {self._construction_home_count}")

        self._tree_count: int = grid.get_structure_count(Tree)
        logger.debug(f"Tree count: {self._tree_count}")
