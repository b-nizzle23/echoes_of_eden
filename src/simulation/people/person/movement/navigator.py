from typing import Optional, List, Dict, Callable, Set, Tuple

import numpy as np
from numpy.ma.core import argmax

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
        self._moving_to_structure_type: Optional[StructureType] = None
        self._visited_structures: Set[Structure] = set()
        self._searched_structure_count: int = 0
        self._structure: Optional[Structure] = None
        self._mover: Mover = Mover(
            simulation.get_grid(), person, self._person.get_memories(), 10
        )
        self._turn_count: int = 0

        actions_per_year: int = self._simulation.actions_per_year()
        self._epsilon_reset: int = int(np.random.uniform(50, actions_per_year))

        self._epsilon: Dict[StructureType, float] = {}
        # used for the epsilon greedy algorithm
        self._rewards: Dict[StructureType, Dict[Location, float]] = {}
        # number of times a person visits a structure and receives a reward
        # also used for epsilon greedy algorithm
        self._actions: Dict[StructureType, Dict[Location, int]] = {}

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
        self._visited_structures.clear()
        self._searched_structure_count = 0
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
        self._moving_to_structure_type = StructureType.HOME
        self._visited_structures.clear()
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
        if self._moving_to_structure_type != structure_type:     # If I have founda valid working structure
            self._reset_moving_state(structure_type)

        self._turn_count += 1

        if not self._structure:     # if I haven't found a work structure yet...
            failed, self._structure = self._find_and_move_to_structure(structure_type)
            if failed:
                return MoveResult(failed, None)     # class that wraps bool

        if self._is_structure_nearby_and_has_capacity(resource_name):   # once you have building and it's nearby and it has capacity
            return MoveResult(False, self._structure)

        return MoveResult(False, None)

    def update_reward(self, y: float) -> None:
        """update the reward given the yield"""
        if not self._moving_to_structure_type or not self._structure:
            return 
        if not self._moving_to_structure_type == StructureType.FARM or not self._moving_to_structure_type == StructureType.TREE or not self._moving_to_structure_type == StructureType.MINE:
            return
        rewards = self._rewards[self._moving_to_structure_type]
        actions = self._actions[self._moving_to_structure_type]
        location = self._structure.get_location()
        rewards[location] += (y - (self._turn_count * 2)) / actions[location]

    def _reset_moving_state(self, building_type: Optional[StructureType]) -> None:      # set all barn data back to zero after transporting all of the resources. 
        """Reset the state when moving to a different building type."""
        self._moving_to_structure_type = building_type
        self._visited_structures.clear()
        self._searched_structure_count = 0
        self._structure = None
        self._turn_count = 0

    def _find_and_move_to_structure(
        self, structure_type: StructureType
    ) -> Tuple[bool, Optional[Structure]]:
        """Find and move to the specified structure type."""
        building_data: Dict[StructureType, Callable[[], Set[Location]]] = (
            self._get_structure_locations()
        )
        construction_tasks: Dict[StructureType, TaskType] = (
            self._get_start_construction_tasks()
        )
        """Find and move to the specified structure construction type."""
        construction_site_data: Dict[StructureType, Callable[[], Set[Location]]] = (
            self._get_construction_structure_locations()
        )
        build_tasks: Dict[StructureType, TaskType] = (
            self._get_construction_tasks()
        )

        if structure_type not in building_data:
            raise Exception(f"Unknown structure type: {structure_type}")

        locations: List[Location] = list(building_data[structure_type]())
        construction_type: Optional[TaskType] = construction_tasks.get(structure_type)
        construction_sites: List[Location] = list(construction_site_data[structure_type]())
        build_type: Optional[TaskType] = build_tasks.get(structure_type)
        
        if structure_type == StructureType.FARM or structure_type == StructureType.TREE or structure_type == StructureType.MINE:
            structure = self._move_to_chosen_structure(structure_type, locations)
        else:
            structure = self._move_to_closet_structure(locations)

        if (
            structure_type != StructureType.TREE
            and not structure
            and self._searched_structure_count >= (len(locations) * 0.37)
        ):

            if len(construction_sites) > 0:
                # construct those structure
                self._person.get_scheduler().add(build_type)
            else:
                # begin construction on a structure of that type
                self._person.get_scheduler().add(construction_type)
            return True, None

        return False, structure

    def _get_structure_locations(
        self,
    ) -> Dict[StructureType, Callable[[], Set[Location]]]:
        """Return the locations of various structures."""
        return {
            StructureType.FARM: self._person.get_memories().get_farm_locations,
            StructureType.MINE: self._person.get_memories().get_mine_locations,
            StructureType.BARN: self._person.get_memories().get_barn_locations,
            StructureType.HOME: self._person.get_memories().get_home_locations,
            StructureType.TREE: self._person.get_memories().get_tree_locations,
        }

    def _get_construction_structure_locations(
        self,
    ) -> Dict[StructureType, Callable[[], Set[Location]]]:
        """Return the locations of various construction sites."""
        return {
            StructureType.FARM: self._person.get_memories().get_farm_construction_locations,
            StructureType.MINE: self._person.get_memories().get_mine_construction_locations,
            StructureType.BARN: self._person.get_memories().get_barn_construction_locations,
            StructureType.HOME: self._person.get_memories().get_home_construction_locations,
        }

    @staticmethod
    def _get_start_construction_tasks() -> Dict[StructureType, TaskType]:
        """Return the construction tasks for each building type."""
        return {
            StructureType.FARM: TaskType.START_FARM_CONSTRUCTION,
            StructureType.MINE: TaskType.START_MINE_CONSTRUCTION,
            StructureType.BARN: TaskType.START_BARN_CONSTRUCTION,
            StructureType.HOME: TaskType.START_HOME_CONSTRUCTION,
        }

    @staticmethod
    def _get_construction_tasks() -> Dict[StructureType, TaskType]:
        """Return the build tasks for each construction site."""
        return {
            StructureType.FARM: TaskType.BUILD_FARM,
            StructureType.MINE: TaskType.BUILD_MINE,
            StructureType.BARN: TaskType.BUILD_BARN,
            StructureType.HOME: TaskType.BUILD_HOME,
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
                self._visited_structures.add(self._structure)
        return False

    def _move_to_closet_structure(self, locations: List[Location]) -> Optional[Structure]:
        """Move to the closest building from the provided locations."""
        visited_buildings_locations: List[Location] = [
            b.get_location() for b in self._visited_structures
        ]
        filtered: List[Location] = [
            l for l in locations if l not in visited_buildings_locations
        ]
        closest: Location = self._mover.get_closest(filtered)
        return self._move_to(closest)
    
    def _move_to_chosen_structure(self, structure_type: StructureType, locations: List[Location]) -> Optional[Structure]:
        """Move to the chosen building that is workable."""
        self._calculate_epsilon(structure_type)

        actions, rewards = self._update_rewards_and_actions(locations, structure_type)

        if np.random.uniform(0,1) < self._epsilon[structure_type]:
            chosen: Location = np.random.choice(list(rewards.keys())) # explore
        else:
            chosen: Location = max(rewards, key=rewards.get) # exploit
        
        actions[chosen] += 1
        
        return self._move_to(chosen)

    def _calculate_epsilon(self, structure_type: StructureType) -> None:
        if not self._epsilon[structure_type]:
            self._epsilon.update({structure_type: 1})

        action_count = sum(list(self._actions[structure_type].values()))

        self._epsilon[structure_type] = self._logarithmic_decay(action_count)

        if self._person.get_time() - action_count > self._epsilon_reset:
            self._epsilon[structure_type] = 1
    
    @staticmethod
    def _logarithmic_decay(t, a=0.5):
        return argmax(0.1 , 1 / (1 + a * np.log(t + 1)))

    def _update_rewards_and_actions(self, locations, structure_type):
        rewards: Dict[Location, float] = self._rewards[structure_type]
        if not rewards:
            self._rewards.update({structure_type: {}})
            rewards = self._rewards[structure_type]
        for location in locations:
            reward = rewards[location]
            if not reward:
                rewards.update({location: 0})
        actions: Dict[Location, int] = self._actions[structure_type]
        if not actions:
            self._actions.update({structure_type: {}})
            actions = self._actions[structure_type]
        for location in locations:
            action = actions[location]
            if not action:
                actions.update({location: 0})
        return actions, rewards
    
    def _move_to(self, location: Location) -> Optional[Structure]:
        self._mover.towards(location)
        return self._simulation.get_grid().get_structure(location)
