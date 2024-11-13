from typing import Optional, List, Dict, Callable, Set, Tuple
from src.simulation.grid.location import Location
from src.simulation.grid.structure.store.home import Home
from src.simulation.grid.structure.store.store import Store
from src.simulation.grid.structure.structure import Structure
from src.simulation.grid.structure.structure_type import StructureType
from src.simulation.people.person.movement.move_result import MoveResult
from src.simulation.people.person.movement.mover import Mover
from src.simulation.people.person.person import Person
from src.simulation.people.person.scheduler.task.task_type import TaskType
from src.simulation.simulation import Simulation


class Navigator:
    def __init__(self, simulation: Simulation, person: Person) -> None:
        """Initialize the Navigator with references to Simulation and Person."""
        self._simulation: Simulation = simulation  # Direct reference to Simulation
        self._person: Person = person
        self._moving_to_building_type: Optional[StructureType] = None
        self._visited_buildings: Set[Structure] = set()
        self._searched_building_count: int = 0
        self._structure: Optional[Structure] = None
        self._mover: Mover = Mover(
            simulation.get_grid(), person, self._person.get_memory(), 10
        )

    def is_stuck(self) -> bool:
        """Determine if the person is stuck and can't move."""
        location: Optional[Location] = (
            self._simulation.get_grid().get_open_spot_next_to_town()
        )
        if not location:
            return True
        return self._mover.can_get_to_location(location)

    def go_to_location(self, location: Location):
        """Move directly to the specified location."""
        self._reset_moving_state(None)
        self._structure = None
        self._mover.towards(location)

    def explore(self) -> None:
        """Explore the area to search for buildings."""
        self._reset_moving_state(None)
        self._visited_buildings.clear()
        self._searched_building_count = 0
        self._mover.explore()

    def move_to_time_estimate(self) -> int:
        """Estimate the time to move to the current building."""
        if not self._structure:
            return 5  # Default estimate if no building is set
        return (
                self._structure.get_location().distance_to(self._person.get_location()) // 10
        )

    def move_to_home(self) -> Optional[Home]:
        """Move towards home, if it's set."""
        self._moving_to_building_type = StructureType.HOME
        self._visited_buildings.clear()
        self._structure = self._person.get_home()
        self._mover.towards(self._structure.get_location())

        # Check if already at home
        if self._person.get_location().is_one_away(self._structure.get_location()):
            self._reset_moving_state(None)
            return self._structure  # Return the home structure
        return None

    def move_to_workable_structure(
        self, structure_type: StructureType, resource_name: Optional[str] = None
    ) -> MoveResult:
        """Move to a building that is workable (e.g., has capacity or resources)."""
        if self._moving_to_building_type != structure_type:     # If I have founda valid working structure
            self._reset_moving_state(structure_type)

        if not self._structure:     # if I haven't found a work structure yet...
            failed, self._structure = self._find_and_move_to_structure(structure_type)
            if failed:
                return MoveResult(failed, None)     # class that wraps bool

        if self._is_structure_nearby_and_has_capacity(resource_name):   # once you have building and it's nearby and it has capacity
            return MoveResult(False, self._structure)

        return MoveResult(False, None)

    def _reset_moving_state(self, building_type: Optional[StructureType]) -> None:      # set all barn data back to zero after transporting all of the resources. 
        """Reset the state when moving to a different building type."""
        self._moving_to_building_type = building_type
        self._visited_buildings.clear()
        self._searched_building_count = 0
        self._structure = None

    def _find_and_move_to_structure(
        self, building_type: StructureType
    ) -> Tuple[bool, Optional[Structure]]:
        """Find and move to the specified building type."""
        building_data: Dict[StructureType, Callable[[], Set[Location]]] = (
            self._get_structure_locations()
        )
        construction_tasks: Dict[StructureType, TaskType] = (
            self._get_construction_tasks()
        )

        # TODO: before you start construction on a new building, check to see if there are already
        #  buildings of that type under construction. And if there is, go build one of those
        if building_type not in building_data:
            raise Exception(f"Unknown structure type: {building_type}")

        buildings: List[Location] = list(building_data[building_type]())
        construction_type: Optional[TaskType] = construction_tasks.get(building_type)

        building = self._move_to(buildings)

        if (
            building_type != StructureType.TREE
            and not building
            and self._searched_building_count >= (len(buildings) * 0.37)
        ):
            self._person.get_scheduler().add(construction_type)
            return True, None

        return False, building

    def _get_structure_locations(
        self,
    ) -> Dict[StructureType, Callable[[], Set[Location]]]:
        """Return the locations of various structures."""
        return {
            StructureType.FARM: self._person.get_memory().get_farm_locations,
            StructureType.MINE: self._person.get_memory().get_mine_locations,
            StructureType.BARN: self._person.get_memory().get_barn_locations,
            StructureType.HOME: self._person.get_memory().get_home_locations,
            StructureType.TREE: self._person.get_memory().get_tree_locations,
        }

    @staticmethod
    def _get_construction_tasks() -> Dict[StructureType, TaskType]:
        """Return the construction tasks for each building type."""
        return {
            StructureType.FARM: TaskType.START_FARM_CONSTRUCTION,
            StructureType.MINE: TaskType.START_MINE_CONSTRUCTION,
            StructureType.BARN: TaskType.START_BARN_CONSTRUCTION,
            StructureType.HOME: TaskType.START_HOME_CONSTRUCTION,
        }

    def _is_structure_nearby_and_has_capacity(
        self, resource_name: Optional[str]
    ) -> bool:
        """Check if the building is nearby and has capacity.""" 
        if self._person.get_location().is_one_away(self._structure.get_location()):     # check if this structure is a barn. if so, grab some food out of it.
            if resource_name and isinstance(self._structure, Store):
                return self._structure.get_resource(resource_name) > 0
            elif self._structure.has_capacity():        # the decision for what task to do based on personal preferences and gathered data. decide to build a structure or not
                self._reset_moving_state(None)
                return True
            else:
                self._visited_buildings.add(self._structure)
        return False

    def _move_to(self, locations: List[Location]) -> Optional[Structure]:
        """Move to the closest building from the provided locations."""
        visited_buildings_locations: List[Location] = [
            b.get_location() for b in self._visited_buildings
        ]
        filtered: List[Location] = [
            l for l in locations if l not in visited_buildings_locations
        ]
        closest: Location = self._mover.get_closest(filtered)
        self._mover.towards(closest)
        return self._simulation.get_grid().get_structure(closest)
