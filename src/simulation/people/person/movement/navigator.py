from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING, Callable, Dict, List, Optional, Set, Tuple

import numpy as np

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
    from src.logger import logger


class Navigator:
    def __init__(self, simulation: Simulation, person: Person) -> None:
        logger.info("Initializing Navigator for person: %s", person.get_name())

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
        logger.debug("Epsilon reset value initialized to: %d", self._epsilon_reset)

        # Using defaultdict to simplify reward and action initialization
        self._epsilon = defaultdict(lambda: 1.0)  # Default epsilon to 1.0
        self._rewards = defaultdict(lambda: defaultdict(float))
        self._actions = defaultdict(lambda: defaultdict(int))

    def is_stuck(self) -> bool:
        logger.info("Checking if navigator is stuck.")
        location = self._simulation.get_grid().get_open_spot_next_to_town()

        stuck = not location or not self._mover.can_get_to(location)
        if stuck:
            logger.warning("Navigator is stuck, no reachable location found.")
        return stuck

    def move_to_time_estimate(self) -> int:
        """Estimate the time to move to the current building."""
        logger.info("Estimating move-to time.")
        if not self._structure:
            logger.debug("No structure set, returning default time estimate of 5.")
            return 5  # Default estimate if no building is set
        time_estimate = self._structure.get_location().distance_to(self._person.get_location()) // settings.get("speed", 10)
        logger.debug("Estimated time to move to the current structure: %d", time_estimate)
        return time_estimate

    def move_to_location(self, location: Location):
        """Move directly to the specified location."""
        logger.info("Navigator moving to location: %s", location)
        self._reset_moving_state(None)
        self._mover.towards(location)

    def explore(self):
        """Explore the area to search for buildings."""
        logger.info("Exploring the area to search for buildings.")
        self._reset_moving_state(None)
        self._mover.explore()

    def move_to_home(self) -> Optional[Home]:
        """Move towards home, if it's set."""
        logger.info("Attempting to move to home.")
        self._moving_to_structure_type = StructureType.HOME
        self._visited_structures.clear()
        self._structure = self._person.get_home()
        self._mover.towards(self._structure.get_location())

        if self._person.get_location().is_one_away(self._structure.get_location()):
            logger.info("Person is one step away from home. Resetting moving state.")
            self._reset_moving_state(None)
            return self._structure
        logger.debug("Person is not yet at home, still moving.")
        return None

    def move_to_workable_structure(
        self, structure_type: StructureType, resource_name: Optional[str] = None
    ) -> MoveResult:
        """Move to a building that is workable (e.g., has capacity or resources)."""
        logger.info("Moving to workable structure of type: %s", structure_type)
        if self._moving_to_structure_type != structure_type:
            logger.debug("Structure type has changed. Resetting moving state.")
            self._reset_moving_state(structure_type)

        self._turn_count += 1
        logger.debug("Turn count incremented to: %d", self._turn_count)

        if not self._structure:
            logger.debug("No structure set. Attempting to find and move to structure.")
            failed, self._structure = self._find_and_move_to_structure(structure_type)
            if failed:
                logger.warning("Failed to find the structure. Returning failure result.")
                return MoveResult(failed, None)

        if self._is_structure_nearby_and_has_capacity(resource_name):
            logger.info("Found workable structure with capacity.")
            return MoveResult(False, self._structure)

        logger.debug("Structure is not nearby or lacks capacity. Returning failure result.")
        return MoveResult(False, None)

    def update_reward(self, y: float) -> None:
        """Update the reward given the yield."""
        logger.info("Updating the reward given the yield.")
        if not self._moving_to_structure_type or not self._structure:
            logger.debug("No structure to update reward for.")
            return
        if self._moving_to_structure_type not in [StructureType.FARM, StructureType.TREE, StructureType.MINE]:
            logger.debug("Structure type is not relevant for reward update.")
            return
        logger.debug("Updating reward for structure type: %s", self._moving_to_structure_type)
        rewards = self._rewards[self._moving_to_structure_type]
        actions = self._actions[self._moving_to_structure_type]
        location = self._structure.get_location()
        rewards[location] += (y - (self._turn_count * 2)) / actions[location]
        logger.debug("Reward updated for location %s: %f", location, rewards[location])

    def _reset_moving_state(self, building_type: Optional[StructureType]) -> None:
        """Reset the state when moving to a different building type."""
        logger.debug("Resetting moving state for new building type: %s", building_type)
        self._moving_to_structure_type = building_type
        self._visited_structures.clear()
        self._searched_structure_count = 0
        self._structure = None
        self._turn_count = 0

    def _find_and_move_to_structure(self, structure_type: StructureType) -> Tuple[bool, Optional[Structure]]:
        logger.info("Finding and moving to structure of type: %s", structure_type)
        building_data = self._get_structure_locations()
        construction_tasks = self._get_start_construction_tasks()
        construction_site_data = self._get_construction_structure_locations()
        build_tasks = self._get_construction_tasks()

        if structure_type not in building_data:
            logger.error("Unknown structure type: %s", structure_type)
            raise Exception(f"Unknown structure type: {structure_type}")

        locations = list(building_data[structure_type]())
        logger.debug("Retrieved %d known locations for structure type: %s", len(locations), structure_type)

        construction_type = construction_tasks.get(structure_type)
        construction_sites = list(construction_site_data[structure_type]())
        build_type = build_tasks.get(structure_type)

        logger.debug(
            "Construction tasks and sites for structure type %s: tasks=%s, sites=%d",
            structure_type,
            construction_type,
            len(construction_sites),
        )

        if structure_type in [StructureType.FARM, StructureType.TREE, StructureType.MINE]:
            structure = self._move_to_chosen_structure(structure_type, locations)
        else:
            structure = self._move_to_closest_structure(locations)

        if (
            structure_type != StructureType.TREE
            and not structure
            and self._searched_structure_count >= (len(locations) * 0.37)
        ):
            if construction_sites:
                self._person.get_scheduler().add(build_type)
            else:
                self._person.get_scheduler().add(construction_type)
            return True, None

        logger.info("Successfully moved to structure of type: %s", structure_type)
        return False, structure

    def _get_structure_locations(self) -> Dict[StructureType, Callable[[], Set[Location]]]:
        """Return the locations of various structures."""
        return {
            StructureType.FARM: self._person.get_memories().get_farm_locations,
            StructureType.MINE: self._person.get_memories().get_mine_locations,
            StructureType.BARN: self._person.get_memories().get_barn_locations,
            StructureType.HOME: self._person.get_memories().get_home_locations,
            StructureType.TREE: self._person.get_memories().get_tree_locations,
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
        logger.info("Checking if structure %s is nearby and has capacity.", self._structure)
        if self._person.get_location().is_one_away(self._structure.get_location()):
            if resource_name and isinstance(self._structure, Store):
                resource_quantity = self._structure.get_resource(resource_name)
                logger.debug(
                    "Resource '%s' in structure: %d available.", resource_name, resource_quantity
                )
                return resource_quantity > 0
            elif self._structure.has_capacity():
                logger.debug("Structure has capacity. Resetting moving state.")
                self._reset_moving_state(None)
                return True
            else:
                logger.warning("Structure %s is full. Marking as visited.", self._structure)
                self._visited_structures.add(self._structure)
        return False

    def _move_to_closest_structure(self, locations: List[Location]) -> Optional[Structure]:
        """Move to the closest building from the provided locations."""
        logger.info("Finding the closest structure from %d locations.", len(locations))
        visited_buildings_locations = [b.get_location() for b in self._visited_structures]
        filtered = [l for l in locations if l not in visited_buildings_locations]
        logger.debug("Filtered to %d unvisited locations.", len(filtered))

        closest = self._mover.get_closest(filtered)
        if closest:
            logger.info("Closest structure found at location %s. Moving to it.", closest)
        else:
            logger.warning("No suitable structure found among the given locations.")
        return self._move_to(closest)

    def _move_to_chosen_structure(
        self, structure_type: StructureType, locations: List[Location]
    ) -> Optional[Structure]:
        """Move to the chosen building that is workable."""
        logger.info("Choosing structure of type %s from %d locations.", structure_type, len(locations))
        self._calculate_epsilon(structure_type)

        actions, rewards = self._update_rewards_and_actions(locations, structure_type)
        logger.debug(
            "Actions: %s | Rewards: %s | Epsilon: %.4f", actions, rewards, self._epsilon[structure_type]
        )

        if np.random.uniform(0, 1) < self._epsilon[structure_type]:
            chosen = np.random.choice(list(rewards.keys()))  # explore
            logger.info("Exploring. Randomly chose location %s.", chosen)
        else:
            chosen = max(rewards, key=rewards.get)  # exploit
            logger.info("Exploiting. Chose location %s with highest reward %.4f.", chosen, rewards[chosen])

        actions[chosen] += 1

        return self._move_to(chosen)

    def _calculate_epsilon(self, structure_type: StructureType) -> None:
        actions = self._actions[structure_type]
        action_count = sum(actions.values())
        logger.debug("Total actions taken for %s: %d.", structure_type, action_count)

        # Update epsilon value based on action count
        self._epsilon[structure_type] = self._logarithmic_decay(action_count)
        logger.debug(
            "Updated epsilon for structure type %s to %.4f based on action count.", structure_type, self._epsilon[structure_type]
        )

        if self._person.get_time() - action_count > self._epsilon_reset:
            logger.info(
                "Time since last action exceeds reset threshold (%d > %d). Resetting epsilon and clearing actions.",
                self._person.get_time() - action_count,
                self._epsilon_reset,
            )
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

        logger.debug("Updating rewards and actions for %s structure type.", structure_type)
        logger.debug("Initial rewards: %s", rewards)
        logger.debug("Initial actions: %s", actions)

        for location in locations:
            rewards.setdefault(location, 0)
            actions.setdefault(location, 0)
            logger.debug("Location %s | Reward: %d | Actions: %d", location, rewards[location], actions[location])

        logger.debug("Updated rewards: %s", rewards)
        logger.debug("Updated actions: %s", actions)

        return actions, rewards

    def _move_to(self, location: Location) -> Optional[Structure]:
        """Move towards the specified location and return the structure at that location."""
        logger.info("Moving towards location: %s", location)
        self._mover.towards(location)

        structure = self._simulation.get_grid().get_structure(location)
        if structure:
            logger.info("Arrived at location %s and found structure: %s", location, structure)
        else:
            logger.warning("Arrived at location %s, but no structure found.", location)

        return structure
