from __future__ import annotations

import random
from typing import TYPE_CHECKING, Callable, Dict, List, Optional, Set, Tuple

import numpy as np
from src.logger import logger

from src.settings import settings
from src.simulation.grid.structure.structure_type import StructureType
from src.simulation.people.person.movement.move_result import MoveResult
from src.simulation.people.person.movement.mover import Mover
from src.simulation.people.person.scheduler.task.task_type import TaskType

if TYPE_CHECKING:
    from src.simulation.grid.location import Location
    from src.simulation.grid.structure.store.home import Home
    from src.simulation.grid.structure.store.store import Store
    from src.simulation.grid.structure.structure import Structure
    from src.simulation.people.person.person import Person
    from src.simulation.simulation import Simulation


class Navigator:
    def __init__(self, simulation: Simulation, person: Person) -> None:
        logger.debug(f"Initializing Navigator for person: {person.get_name()}")

        self._simulation = simulation
        self._person = person
        self._moving_to_structure_type: Optional[StructureType] = None
        self._visited_structures: Set[Structure] = set()
        self._searched_structure_count: int = 0
        self._structure: Optional[Structure] = None
        self._mover: Mover = Mover(simulation.get_grid(), person, person.get_memories(), settings.get("speed", 10))
        self._turn_count: int = 0

        # when to start looking for new place of work
        actions_per_year = simulation.actions_per_year()
        self._epsilon_reset = int(np.random.uniform(50, actions_per_year))
        logger.debug(f"Epsilon reset value initialized to: {self._epsilon_reset}")

        # Using defaultdict to simplify reward and action initialization
        self._epsilon: Dict[StructureType, float] = {}
        self._rewards: Dict[StructureType, Dict[Location, float]] = {}
        self._actions: Dict[StructureType, Dict[Location, int]] = {}
        for structure_type in StructureType:
            self._rewards[structure_type] = {}
            self._actions[structure_type] = {}

    def is_stuck(self) -> bool:
        logger.debug("Checking if navigator is stuck.")
        locations: List[Location] = self._simulation.get_grid().get_empty_spots_near_town()
        location: Location = random.choice(locations)
        while location == self._person.get_location():
            location: Location = random.choice(locations)

        stuck = not self._mover.can_get_to(location)
        if stuck:
            logger.warning("Navigator is stuck, no reachable location found.")
        return stuck

    def move_to_time_estimate(self) -> int:
        """Estimate the time to move to the current building."""
        logger.debug("Estimating move-to time.")
        if not self._structure:
            logger.debug("No structure set, returning default time estimate of 5.")
            return 5  # Default estimate if no building is set
        time_estimate = self._structure.get_location().distance_to(self._person.get_location()) // settings.get("speed", 10)
        logger.debug(f"Estimated time to move to the current structure: {time_estimate}")
        return time_estimate

    def move_to_location(self, location: Location):
        """Move directly to the specified location."""
        logger.debug(f"Navigator moving to location: {location}")
        self._reset_moving_state(None)
        self._mover.towards(location)

    def explore(self):
        """Explore the area to search for buildings."""
        logger.debug("Exploring the area to search for buildings.")
        self._reset_moving_state(None)
        self._mover.explore()

    def move_to_home(self) -> Optional[Home]:
        """Move towards home, if it's set."""
        logger.debug("Attempting to move to home.")
        self._moving_to_structure_type = StructureType.HOME
        self._visited_structures.clear()
        self._structure = self._person.get_home()
        self._mover.towards(self._structure.get_location())

        if self._person.get_location().is_one_away(self._structure.get_location()):
            logger.debug("Person is one step away from home. Resetting moving state.")
            self._reset_moving_state(None)
            return self._structure
        logger.debug("Person is not yet at home, still moving.")
        return None

    def move_to_workable_structure(
        self, structure_type: StructureType, resource_name: Optional[str] = None
    ) -> MoveResult:
        """Move to a building that is workable (e.g., has capacity or resources)."""
        logger.debug(f"Moving to workable structure of type: {structure_type}")
        if self._moving_to_structure_type != structure_type:
            logger.debug("Structure type has changed. Resetting moving state.")
            self._reset_moving_state(structure_type)

        self._turn_count += 1
        logger.debug(f"Turn count incremented to: {self._turn_count}")

        if not self._structure:
            logger.debug("No structure set. Attempting to find and move to structure.")
            failed, self._structure = self._find_and_move_to_structure(structure_type)
            if failed:
                logger.warning("Failed to find the structure. Returning failure result.")
                return MoveResult(failed, None)
        
        if not self._structure:
            return MoveResult(True, None)
        if self._is_structure_nearby_and_has_capacity(resource_name):
            logger.debug("Found workable structure with capacity.")
            return MoveResult(False, self._structure)

        logger.debug("Structure is not nearby or lacks capacity. Returning failure result.")
        return MoveResult(True, None)

    def update_reward(self, y: float) -> None:
        """Update the reward given the yield."""
        logger.debug("Updating the reward given the yield.")
        if not self._moving_to_structure_type or not self._structure:
            logger.debug("No structure to update reward for.")
            return
        if self._moving_to_structure_type not in [StructureType.FARM, StructureType.TREE, StructureType.MINE]:
            logger.debug("Structure type is not relevant for reward update.")
            return
        logger.debug(f"Updating reward for structure type: {self._moving_to_structure_type}")
        rewards = self._rewards[self._moving_to_structure_type]
        actions = self._actions[self._moving_to_structure_type]
        location = self._structure.get_location()
        rewards[location] += (y - (self._turn_count * 2)) / actions[location]
        logger.debug(f"Reward updated for location {location}: {rewards[location]}")

    def _reset_moving_state(self, building_type: Optional[StructureType]) -> None:
        """Reset the state when moving to a different building type."""
        logger.debug(f"Resetting moving state for new building type: {building_type}")
        self._moving_to_structure_type = building_type
        self._visited_structures.clear()
        self._searched_structure_count = 0
        self._structure = None
        self._turn_count = 0

    def _find_and_move_to_structure(self, structure_type: StructureType) -> Tuple[bool, Optional[Structure]]:
        logger.debug(f"Finding and moving to structure of type: {structure_type}")
        structure_data = self._get_structure_locations()
        if structure_type not in structure_data:
            logger.error(f"Unknown structure type: {structure_type}")
            raise Exception(f"Unknown structure type: {structure_type}")

        locations = list(structure_data[structure_type]())
        logger.debug(f"Retrieved {len(locations)} known locations for structure type: {structure_type}")
        
        if locations:
            if structure_type in [StructureType.FARM, StructureType.TREE, StructureType.MINE]:
                structure = self._move_to_chosen_structure(structure_type, locations)
            else:
                structure = self._move_to_closest_structure(locations)
        else:
            structure = None
        
        if (
            structure_type != StructureType.TREE and 
                (not structure or self._searched_structure_count >= (len(locations) * 0.37))
        ):
            construction_tasks = self._get_start_construction_tasks()
            construction_site_data = self._get_construction_structure_locations()
            build_tasks = self._get_construction_tasks()
            if structure_type not in list(build_tasks.keys()):
                logger.warning("You couldn't find a construction site even tho we only add build tasks when you know about construction sites")
                return True, None
    
            construction_type = construction_tasks.get(structure_type)
            construction_sites = list(construction_site_data[structure_type]())
            build_type = build_tasks.get(structure_type)
        
            if construction_sites:
                self._person.get_scheduler().add(build_type)
            else:
                self._person.get_scheduler().add(construction_type)
            return True, None

        logger.debug(f"Successfully moved to structure of type: {structure_type}")
        return False, structure

    def _get_structure_locations(self) -> Dict[StructureType, Callable[[], Set[Location]]]:
        """Return the locations of various structures."""
        return {
            StructureType.FARM: self._person.get_memories().get_farm_locations,
            StructureType.MINE: self._person.get_memories().get_mine_locations,
            StructureType.BARN: self._person.get_memories().get_barn_locations,
            StructureType.HOME: self._person.get_memories().get_home_locations,
            StructureType.TREE: self._person.get_memories().get_tree_locations,
            StructureType.CONSTRUCTION_BARN: self._person.get_memories().get_barn_construction_locations,
            StructureType.CONSTRUCTION_FARM: self._person.get_memories().get_farm_construction_locations,
            StructureType.CONSTRUCTION_HOME: self._person.get_memories().get_home_construction_locations,
            StructureType.CONSTRUCTION_MINE: self._person.get_memories().get_mine_construction_locations,
        }

    def _get_construction_structure_locations(self) -> Dict[StructureType, Callable[[], Set[Location]]]:
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

    def _is_structure_nearby_and_has_capacity(self, resource_name: Optional[str]) -> bool:
        """Check if the building is nearby and has capacity."""
        logger.debug(f"Checking if structure {self._structure} is nearby and has capacity.")
        if self._person.get_location().is_one_away(self._structure.get_location()):
            if resource_name and isinstance(self._structure, Store):
                resource_quantity = self._structure.get_resource(resource_name)
                logger.debug(f"Resource {resource_name} in structure: {resource_quantity} available.")
                return resource_quantity > 0
            elif self._structure.has_capacity():
                logger.debug("Structure has capacity. Resetting moving state.")
                self._reset_moving_state(None)
                return True
            else:
                logger.warning(f"Structure {self._structure} is full. Marking as visited.")
                self._visited_structures.add(self._structure)
        return False

    def _move_to_closest_structure(self, locations: List[Location]) -> Optional[Structure]:
        """Move to the closest building from the provided locations."""
        logger.debug(f"Finding the closest structure from {len(locations)} locations.")
        visited_buildings_locations = [b.get_location() for b in self._visited_structures]
        filtered = [l for l in locations if l not in visited_buildings_locations]
        logger.debug(f"Filtered to {len(filtered)} unvisited locations.")

        closest = self._mover.get_closest(filtered)
        if closest:
            logger.debug(f"Closest structure found at location {closest}. Moving to it.")
        else:
            logger.warning("No suitable structure found among the given locations.")
        return self._move_to(closest)

    def _move_to_chosen_structure(
        self, structure_type: StructureType, locations: List[Location]
    ) -> Optional[Structure]:
        """Move to the chosen building that is workable."""
        logger.debug(f"Choosing structure of type {structure_type} from {len(locations)} locations.")

        actions, rewards = self._update_rewards_and_actions(locations, structure_type)
        
        self._calculate_epsilon(structure_type)

        logger.debug(f"Actions: {actions} | Rewards: {rewards} | Epsilon: {self._epsilon[structure_type]:.4f}")

        if np.random.uniform(0, 1) < self._epsilon[structure_type]:
            chosen = np.random.choice(list(rewards.keys()))  # explore
            logger.debug(f"Exploring. Randomly chose location {chosen}.")
        else:
            chosen = max(rewards, key=rewards.get)  # exploit
            logger.debug(f"Exploiting. Chose location {chosen} with highest reward {rewards[chosen]:.4f}.")

        actions[chosen] += 1

        return self._move_to(chosen)

    def _calculate_epsilon(self, structure_type: StructureType) -> None:
        actions = self._actions[structure_type]
        action_count = sum(actions.values())
        logger.debug(f"Total actions taken for {structure_type}: {action_count}.")

        # Update epsilon value based on action count
        self._epsilon[structure_type] = self._logarithmic_decay(action_count)
        logger.debug(f"Updated epsilon for structure type {structure_type} to {self._epsilon[structure_type]:.4f} based on action count.")

        if self._person.get_time() - action_count > self._epsilon_reset:
            logger.debug(f"Time since last action exceeds reset threshold ({self._person.get_time() - action_count} > {self._epsilon_reset}). Resetting epsilon and clearing actions.")
            self._epsilon[structure_type] = 1
            actions.clear()

    @staticmethod
    def _logarithmic_decay(t, a=0.5):
        return max(0.1, 1 / (1 + a * np.log(t + 1)))

    def _update_rewards_and_actions(
        self, locations: List[Location], structure_type: StructureType
    ) -> Tuple[Dict[Location, int], Dict[Location, float]]:
        """Update the rewards and actions for each location."""
        rewards = self._rewards[structure_type]
        actions = self._actions[structure_type]

        logger.debug(f"Updating rewards and actions for {structure_type} structure type.")
        logger.debug(f"Initial rewards: {rewards}")
        logger.debug(f"Initial actions: {actions}")

        for location in locations:
            if location in rewards or location in actions:
                continue
            rewards.setdefault(location, 0)
            actions.setdefault(location, 0)
            logger.debug(f"Location {location} | Reward: {rewards[location]} | Actions: {actions[location]}")

        logger.debug(f"Updated rewards: {rewards}")
        logger.debug(f"Updated actions: {actions}")

        return actions, rewards

    def _move_to(self, location: Location) -> Optional[Structure]:
        """Move towards the specified location and return the structure at that location."""
        logger.debug(f"Moving towards location: {location}")
        self._mover.towards(location)

        structure = self._simulation.get_grid().get_structure(location)
        if structure:
            logger.debug(f"Arrived at location {location} and found structure: {structure}")
        else:
            logger.warning(f"Arrived at location {location}, but no structure found.")

        return structure
