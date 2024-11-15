from typing import List, Optional, Dict

import numpy as np
import random

from scheduler.scheduler import Scheduler
from scheduler.task.task_type import TaskType
from src.simulation.grid.structure.store.barn import Barn
from src.simulation.grid.structure.store.home import Home

from src.simulation.grid.structure.structure import Structure
from src.simulation.grid.structure.structure_type import StructureType
from src.simulation.grid.location import Location
from src.simulation.people.person.backpack import Backpack
from src.simulation.people.person.memories import Memories
from src.simulation.people.person.movement.move_result import MoveResult
from src.simulation.people.person.movement.navigator import Navigator
from src.simulation.simulation import Simulation
from src.logger import logger


class Person:
    def __init__(
        self, simulation: Simulation, name: str, pk: int, location: Location, age: int
    ) -> None:
        self._name: str = name
        self._pk: int = pk
        self._age: int = age
        self._simulation = simulation
        self._location: Location = location

        self._backpack = Backpack()
        self._memory: Memories = Memories(simulation.get_grid())
        self._navigator: Navigator = Navigator(simulation, self)

        self._health: int = 100
        self._hunger: int = (
            100  # when your hunger gets below 25, health starts going down; when it gets above 75, health starts going up
        )
        self._home: Optional[Home] = None
        self._spouse: Optional[Person] = None
        self._scheduler: Scheduler = Scheduler(simulation, self)
        self._max_time: int = 10

        # preferences per person
        self._hunger_preference: int = random.randint(50, 100)
        self._spouse_preference: bool = random.choice([True, False])
        self._house_preference: bool = random.choice([True, False])

        # preferences per person
        self._hunger_preference: int = random.randint(50, 100)
        self._spouse_preference: bool = random.choice([True, False])
        self._house_preference: bool = random.choice([True, False])

        self._rewards: Dict[TaskType, int] = {}

        logger.info(f"Initialized Person '{self._name}' with age {self._age}")
        logger.debug(f"Attributes for '{self._name}': health={self._health}, hunger={self._hunger}, preferences={{'hunger': {self._hunger_preference}, 'spouse': {self._spouse_preference}, 'house': {self._house_preference}}}")

    def get_time(self) -> int:
        return self._simulation.get_time()

    def get_backpack(self) -> Backpack:
        return self._backpack

    def get_memory(self) -> Memories:
        return self._memory

    def exchange_memories(self, other: "Person") -> None:
        if not other:
            return
        self._memory.combine(other.get_memory())
        other.get_memory().combine(self._memory)

    def get_empties(self) -> List[Location]:
        return list(self._memory.get_empty_locations())

    def get_buildings(self) -> List[Location]:
        return list(self._memory.get_building_locations())

    def get_scheduler(self) -> Scheduler:
        return self._scheduler

    def get_work_structures(self) -> List[Location]:
        structures: List[Structure] = []
        for task in self._scheduler.get_all_tasks():
            structure: Structure = task.get_work_structure()
            if structure:
                structures.append(structure)
        return list(map(lambda s: s.get_location(), structures))
    
    def get_hunger_preference(self) -> int:
        return self._hunger_preference
    
    def get_spouse_preference(self) -> bool:
        return self._spouse_preference

    def get_house_preference(self) -> bool:
            return self._house_preference

    def kill(self):
        self._health = 0

    def take_action(self) -> None:
        logger.info(f"{self._name} is starting an action with current hunger={self._hunger} and health={self._health}")
        self._hunger -= 1
        logger.debug(f"{self._name}'s hunger decreased by 1 to {self._hunger}")

        if self._hunger < 20:
            self._health -= 1
            logger.debug(f"{self._name}'s health decreased due to being hungry (Health: {self._health})")

        elif self._hunger > 50:
            self._health += 1
            logger.debug(f"{self._name}'s health increased due to being full (Health: {self._health})")

        self._add_tasks()
        self._scheduler.execute()
        logger.debug(f"{self._name} completed action with health={self._health} and hunger={self._hunger}")

    def _add_tasks(self) -> None:   # where tasks are added to the scheduler. 
        logger.info(f"Adding tasks for {self._name}")
        # 1. Find a home
        if not self._home:
            self._scheduler.add(TaskType.FIND_HOME)
            logger.debug(f"{self._name} has no home and added FIND_HOME task")

        # 2. Deliver items you are carrying
        if self._backpack.has_items():
            self._scheduler.add(TaskType.TRANSPORT)
            logger.debug(f"{self._name} has items in backpack and added TRANSPORT task")

        # Things to check only so often
        if self._simulation.get_people().get_time() % self._max_time == 0:
            # 3. Find a spouse
            if not self._spouse and self._spouse_preference:
                self._scheduler.add(TaskType.FIND_SPOUSE)
                logger.debug(f"{self._name} prefers a spouse and added FIND_SPOUSE task")

            # 4. Eat food
            if self._hunger < self._hunger_preference:
                self._scheduler.add(TaskType.EAT)
                logger.debug(f"{self._name} is hungry and added EAT task")

            # 5. Find a home
            if not self.has_home() and self._house_preference:
                self._scheduler.add(TaskType.FIND_HOME)
                logger.debug(f"{self._name} prefers a home and added FIND_HOME task")

        # 6. Epsilon-Greedy algorithm to decide what work to do
        self._add_work_tasks()

        # 7. If you've got nothing else to do, explore
        if len(self._scheduler.get_tasks()) == 0:
            self._scheduler.add(TaskType.EXPLORE)
            logger.debug(f"{self._name} has no tasks and added EXPLORE task")

    def _add_work_tasks(self) -> None:
        if not self._backpack.has_capacity():
            logger.debug(f"{self._name}'s backpack is full; no work task added")
            return
        keys: list = list(self._rewards.keys())
        epsilon: float = 0.05
        if np.random.rand() < epsilon:
            # Exploration: randomly select an action
            random_index: int = np.random.randint(0, len(keys) - 1)
            task_type: TaskType = keys[random_index]
            logger.debug(f"{self._name} is exploring by selecting random task: {task_type}")
        else:
            task_type: TaskType = max(self._rewards, key=self._rewards.get)
            logger.debug(f"{self._name} selected highest reward task: {task_type}")

        self._scheduler.add(task_type)
        logger.info(f"{self._name} added task '{task_type}' to scheduler")

    def update_rewards(self, reward: int, task_type: TaskType) -> None:
        old_reward = self._rewards.get(task_type, 0)
        self._rewards[task_type] = old_reward + reward
        logger.debug(f"Updated rewards for {self._name}: '{task_type}' reward changed from {old_reward} to {self._rewards[task_type]}")

    def get_location(self) -> Location:
        return self._location

    def get_health(self) -> int:
        return self._health

    def get_hunger(self) -> int:
        return self._hunger

    def get_home(self) -> Optional[Home]:
        return self._home

    def get_age(self) -> int:
        return self._age

    def set_location(self, other: Location) -> None:
        if not self._simulation.get_grid().is_location_in_bounds(other):
            logger.error(f"{self._name} tried to move outside map bounds to {other}")
            raise Exception("You tried to put a person outside of the map")
        self._location = other
        logger.info(f"{self._name} moved to new location: {self._location}")

    def is_dead(self) -> bool:
        return self._health <= 0 or self._age >= 80

    def is_satiated(self) -> bool:
        return self.get_hunger() >= self.get_hunger_preference()

    def eat(self, building: Barn | Home) -> None:
        if isinstance(building, Home):
            self._hunger = min(self._hunger + 10, 100)
        else:
            self._hunger = min(
                self._hunger + 5, 100
            )  # eating in a barn is less effective
        building.remove_resource("food", 3)

    def set_hunger(self, hunger: int) -> None:
        old_hunger = self._hunger
        self._hunger = max(0, min(self._hunger + hunger, 100))
        logger.debug(f"{self._name}'s hunger adjusted from {old_hunger} to {self._hunger}")

    def assign_spouse(self, spouse: "Person") -> None:
        self._spouse = spouse

    def divorce(self) -> None:
        if not self._spouse:
            logger.warning(f"{self._name} has no spouse to divorce")
            return
        self.get_spouse().leave_spouse()
        self._spouse = None
        logger.info(f"{self._name} has divorced their spouse")

    def leave_spouse(self) -> None:
        self._home = None
        self._spouse = None
        logger.info(f"{self._name} has left their spouse and home")

    def get_spouse(self) -> Optional["Person"]:
        return self._spouse
    
    def assign_home(self, home: Home) -> None:
        if self._home == home:
            logger.debug(f"{self._name} already assigned to home: {home}")
            return
        self._home = home
        home.assign_owner(self)
        logger.info(f"{self._name} assigned to new home: {home}")
        if self.has_spouse():
            self.get_spouse().assign_home(home)
            logger.debug(f"{self._name}'s spouse also assigned to the new home: {home}")

    def remove_home(self):
        if not self._home:
            logger.warning(f"{self._name} has no home to remove")
            return
        self._home = None
        logger.info(f"{self._name} removed from home")
        if self.has_spouse():
            self._spouse.remove_home()
            logger.debug(f"{self._name}'s spouse's home also removed")

    def set_health(self, health: int) -> None:
        old_health = self._health
        self._health = max(0, min(self._health + health, 100))
        logger.debug(f"{self._name}'s health adjusted from {old_health} to {self._health}")

    def has_home(self) -> bool:
        return self._home is not None

    def start_home_construction(self) -> None:
        self._scheduler.add(TaskType.START_HOME_CONSTRUCTION)
        logger.info(f"{self._name} started home construction task")

    def work_farm(self) -> None:
        self._scheduler.add(TaskType.WORK_FARM)
        logger.info(f"{self._name} started work farm task")

    def has_spouse(self) -> bool:
        return self._spouse is not None

    def age(self) -> None:
        self._age += 1

    def get_home_locations(self):
        return self._memory.get_home_locations()

    def is_stuck(self) -> bool:
        return self._navigator.is_stuck()

    def go_to_location(self, location: Location) -> None:
        self._navigator.go_to_location(location)

    def explore(self) -> None:
        """Explore the area to search for buildings."""
        self._navigator.explore()

    def move_to_home(self) -> Optional[Home]:
        """Move towards home, if it's set."""
        return self._navigator.move_to_home()
    
    def get_simulation(self) -> Simulation:
        return self._simulation

    def move_to_workable_structure(
        self, building_type: StructureType, resource_name: Optional[str] = None
    ) -> MoveResult:
        """Move to a building that is workable (e.g., has capacity or resources)."""
        return self._navigator.move_to_workable_structure(building_type, resource_name)

    def move_to_time_estimate(self) -> int:
        """Estimate the time to move to the current building."""
        return self.move_to_time_estimate()
