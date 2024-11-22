from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from src.logger import logger
from src.settings import settings
from src.simulation.people.person.backpack import Backpack
from src.simulation.people.person.memories import Memories
from src.simulation.people.person.movement.navigator import Navigator
from src.simulation.people.person.scheduler.scheduler import Scheduler
from src.simulation.people.person.scheduler.task.task_type import TaskType
from src.simulation.people.person.thinker import Thinker

if TYPE_CHECKING:
    from src.simulation.grid.location import Location
    from src.simulation.grid.structure.store.barn import Barn
    from src.simulation.grid.structure.store.home import Home
    from src.simulation.grid.structure.structure import Structure
    from src.simulation.grid.structure.structure_type import StructureType
    from src.simulation.people.person.movement.move_result import MoveResult
    from src.simulation.simulation import Simulation


class Person:
    def __init__(self, simulation: Simulation, name: str, pk: int, location: Location, age: int) -> None:
        self._name: str = name
        self._pk: int = pk
        self._age: int = age
        self._simulation = simulation
        self._location: Location = location

        # when your hunger gets below 25, health starts going down; when it gets above 75, health starts going up
        self._health: int = settings.get("person_health_cap", 100)
        self._hunger: int = settings.get("person_hunger_cap", 100)

        self._home: Optional[Home] = None
        self._spouse: Optional[Person] = None
        
        self._backpack: Backpack = Backpack()
        self._scheduler: Scheduler = Scheduler(simulation, self)
        self._memories: Memories = Memories(simulation.get_grid())
        self._navigator: Navigator = Navigator(simulation, self)
        self._thinker: Thinker = Thinker(simulation, self)

    def get_task_type_priority(self, task_type: TaskType) -> int:
        return self._thinker.get_task_type_priority(task_type)
        
    def __str__(self) -> str:
        return f"Person({self._pk}, {self._name})"

    def __repr__(self) -> str:
        return f"Person({self._pk}, {self._name})"

    def get_time(self) -> int:
        return self._simulation.get_time()

    def get_backpack(self) -> Backpack:
        return self._backpack

    def get_memories(self) -> Memories:
        return self._memories

    def get_name(self) -> str:
        return self._name

    def exchange_memories(self, other: "Person") -> None:
        if not other:
            return
        self._memories.combine(other.get_memories())
        other.get_memories().combine(self._memories)
        logger.info(f"{self._name} is exchanging memories with {other.get_name()}")

    def get_empties(self) -> List[Location]:
        return list(self._memories.get_empty_locations())

    def get_buildings(self) -> List[Location]:
        return list(self._memories.get_building_locations())

    def get_scheduler(self) -> Scheduler:
        return self._scheduler

    def get_work_structures(self) -> List[Location]:
        logger.info(f"getting all structures {self._name} is working on.")
        structures: List[Structure] = []
        for task in self._scheduler.get_this_years_tasks():
            structure: Structure = task.get_work_structure()
            if structure:
                structures.append(structure)
        return list(map(lambda s: s.get_location(), structures))

    def kill(self):
        self.set_health(-100)

    def take_action(self) -> None:
        self._thinker.take_action()

    def update_scheduler_rewards(self, task_type: TaskType, reward: int) -> None:
        self._thinker.update_scheduler_rewards(task_type, reward)

    def get_hunger_preference(self) -> int:
        return self._thinker.get_hunger_preference()

    def update_navigator_rewards(self, y: float):
        self._navigator.update_reward(y)

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
        if not self._simulation.get_grid().is_in_bounds(other):
            logger.error(f"{self._name} tried to move outside map bounds to {other}")
            return

        self._location = other
        logger.info(f"{self._name} moved to new location: {self._location}")

    def is_dead(self) -> bool:
        return self._health <= 0 or self._age >= settings.get("person_age_max", 80)

    def is_satiated(self) -> bool:
        return self.get_hunger() >= self.get_hunger_preference()

    def eat(self, building: Barn | Home) -> None:
        logger.info(f"{self._name} is about to eat with hunger {self._hunger}")
        if isinstance(building, Home):
            self.set_hunger(settings.get("home_eat_satiate", 15))
            building.remove_resource(settings.get("food", "food"), settings.get("home_eat_satiate", 15))
            logger.debug(f"{self._name} ate at home and their hunger is now {self._hunger}")
        else:
            self.set_hunger(settings.get("barn_eat_satiate", 10))
            building.remove_resource(settings.get("food", "food"), settings.get("barn_eat_satiate", 10))
            logger.debug(f"{self._name} ate in a barn and their hunger is now {self._hunger}")

    def set_hunger(self, hunger: int) -> None:
        old_hunger = self._hunger
        self._hunger = max(0, min(self._hunger + hunger, settings.get("person_hunger_cap", 100)))
        logger.info(f"{self._name}'s hunger adjusted from {old_hunger} to {self._hunger}")

    def assign_spouse(self, spouse: "Person") -> None:
        self._spouse = spouse

    def divorce(self) -> None:
        if not self._spouse:
            logger.warning(f"{self._name} has no spouse to divorce")
            return
        old_spouse: Person = self._spouse
        self.get_spouse().leave_spouse()
        self._spouse = None
        logger.info(f"{self._name} has divorced their spouse {old_spouse}")

    def leave_spouse(self) -> None:
        self._home = None
        self._spouse = None
        logger.info(f"{self._name} has left their spouse and home")

    def get_spouse(self) -> Optional["Person"]:
        return self._spouse

    def assign_home(self, home: Home) -> None:
        if self._home == home:
            return
        self.remove_home()
        self._home = home
        home.assign_owner(self)
        logger.info(f"{self._name} assigned to new home: {home}")
        if self.has_spouse():
            self.get_spouse().assign_home(home)
            logger.debug(f"{self._name}'s spouse also assigned to the new home: {home}")

    def remove_home(self):
        if not self._home:
            logger.warning(f"{self._name} tried to remove home but has no home to remove")
            return
        self._home.assign_owner(None)
        self._home = None
        logger.info(f"{self._name} removed from home")
        if self.has_spouse():
            self._spouse.remove_home()
            logger.debug(f"{self._name}'s spouse's home also removed")

    def set_health(self, health: int) -> None:
        old_health = self._health
        self._health = max(0, min(self._health + health, settings.get("person_health_cap", 100)))
        logger.info(f"{self._name}'s health adjusted from {old_health} to {self._health}")

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

    def is_stuck(self) -> bool:
        return self._navigator.is_stuck()

    def go_to_location(self, location: Location) -> None:
        self._navigator.move_to_location(location)

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
        return self._navigator.move_to_time_estimate()
