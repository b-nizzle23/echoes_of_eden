from __future__ import annotations

import random
from typing import TYPE_CHECKING, Dict, List

import numpy as np

from src.logger import logger
from src.settings import settings
from src.simulation.grid.structure.store.barn import Barn
from src.simulation.people.person.scheduler.task.task_type import TaskType

if TYPE_CHECKING:
    from src.simulation.people.person.person import Person
    from src.simulation.simulation import Simulation


class Thinker:
    def __init__(self, simulation: Simulation, person: Person) -> None:
        self._person: Person = person
        self._simulation: Simulation = simulation
        self._scheduler = person.get_scheduler()

        # preferences per person
        self._hunger_preference: int = random.randint(
            settings.get("hunger_pref_min", 50), settings.get("hunger_pref_max", 100)
        )

        self._work_rewards: Dict[TaskType, int] = {TaskType.WORK_FARM: 0, TaskType.WORK_MINE: 0, TaskType.CHOP_TREE: 0}

        self._task_type_priorities: Dict[TaskType, int] = {
            TaskType.EAT: 10,
            TaskType.FIND_HOME: 6,
            TaskType.EXPLORE: 1,
            TaskType.FIND_SPOUSE: 1,
            TaskType.TRANSPORT: 5,
            TaskType.CHOP_TREE: 2,
            TaskType.WORK_FARM: 4,
            TaskType.WORK_MINE: 2,
            TaskType.BUILD_BARN: 3,
            TaskType.BUILD_HOME: 3,
            TaskType.BUILD_FARM: 3,
            TaskType.BUILD_MINE: 3,
            TaskType.START_FARM_CONSTRUCTION: 1,
            TaskType.START_BARN_CONSTRUCTION: 1,
            TaskType.START_MINE_CONSTRUCTION: 1,
            TaskType.START_HOME_CONSTRUCTION: 1
        }

    def get_hunger_preference(self) -> int:
        return self._hunger_preference
        
    def get_task_type_priority(self, task_type: TaskType) -> int:
        return self._task_type_priorities[task_type]

    def take_action(self) -> None:
        logger.info(f"{self._person.get_name()} is starting an action with current hunger={self._person.get_hunger()} and health={self._person.get_health()}")
        self._person.set_hunger(-1)
        logger.debug(f"{self._person.get_name()}'s hunger decreased by 1 to {self._person.get_hunger()}")

        if self._person.get_hunger() < settings.get("hunger_damage_threshold", 20):
            self._person.set_health(-1)
            logger.debug(f"{self._person.get_name()}'s health decreased due to being hungry (Health: {self._person.get_health()})")
        elif self._person.get_hunger() > settings.get("hunger_regen_threshold", 50):
            self._person.set_health(1)
            logger.debug(f"{self._person.get_name()}'s health increased due to being full (Health: {self._person.get_health()})")

        self._add_tasks()
        self._scheduler.execute()
        self._adjust_priorities()

        logger.debug(f"{self._person.get_name()} completed action with health={self._person.get_health()} and hunger={self._person.get_hunger()}")

    def update_scheduler_rewards(self, task_type: TaskType, reward: int) -> None:
        old_reward = self._work_rewards.get(task_type, 0)
        self._work_rewards[task_type] = old_reward + reward
        logger.debug(
            f"Updated rewards for {self._person.get_name()}: '{task_type}' reward changed from {old_reward} to {self._work_rewards[task_type]}"
        )

    def _add_tasks(self) -> None:  # where tasks are added to the scheduler.
        logger.info(f"Adding tasks for {self._person.get_name()}")
        # check to do this stuff every once in a while
        self._scheduler.add(TaskType.EXPLORE)
        logger.debug(f"{self._person.get_name()} added EXPLORE task")
    
        if not self._person.get_spouse():
            self._scheduler.add(TaskType.FIND_SPOUSE)
            logger.debug(f"{self._person.get_name()} added FIND_SPOUSE task")
    
        if not self._person.get_home():
            self._scheduler.add(TaskType.FIND_HOME)
            logger.debug(f"{self._person.get_name()} added FIND_HOME task")

        # Deliver items you are carrying
        if self._person.get_backpack().has_items():
            self._scheduler.add(TaskType.TRANSPORT)
            logger.debug(f"{self._person.get_name()} has items in backpack and added TRANSPORT task")

        # Epsilon-Greedy algorithm to decide what type of work to do
        if self._person.get_backpack().has_capacity():
            self._add_work_task()
        else:
            logger.debug(f"{self._person.get_name()}'s backpack is full; no work task added")

        if self._person.get_hunger() < self._hunger_preference:
            self._scheduler.add(TaskType.EAT)
            logger.debug(f"{self._person.get_name()} is hungry and added EAT task")

    def _add_work_task(self) -> None:
        keys: List[TaskType] = list(self._work_rewards.keys())
        epsilon: float = settings.get("person_epsilon", 0.05)
        if np.random.rand() < epsilon or all(value == 0 for value in self._work_rewards.values()):
            random_index: int = np.random.randint(0, len(keys) - 1)
            task_type: TaskType = keys[random_index]
            logger.debug(f"{self._person.get_name()} is exploring by selecting random task: {task_type}")
        else:
            task_type: TaskType = max(self._work_rewards, key=self._work_rewards.get)
            logger.debug(f"{self._person.get_name()} selected highest reward task: {task_type}")

        self._scheduler.add(task_type)
        logger.info(f"{self._person.get_name()} added task '{task_type}' to scheduler")

    def _adjust_priorities(self) -> None:
        # explore should be high if they dont have a lot of memories
        self._set_explore_priority()

        # start construction tasks should just always be high, but explore should be bigger if we dont have a lot of memories
        self._set_start_construction_task_priorities()

        # the more full the backpack the higher the transport task is
        self._set_transport_priority()

        # the less food, wood, and stone in the barn, the more we need to work_farm, chop_tree, and work_mine relative to barn capacities
        self._set_resource_gathering_priorities()

        # the more construction sites there are the more of a need to build them
        self._set_barn_construction_priorities()
        self._set_farm_construction_priorities()
        self._set_home_construction_priorities()
        self._set_mine_construction_priorities()

        # TODO find home should be higher the longer you dont have a home but make sure that construction tasks are higher

        # TODO eat should be higher the more hungry you are but only if their is food in the barns or at home
        
        # at the end of this we need to make sure that generally
        # explore > start_construction > transport > resource_gathering > eat > construction > find_home

    def _set_explore_priority(self):
        # Get the grid dimensions
        grid_width = self._simulation.get_grid().get_width()
        grid_height = self._simulation.get_grid().get_height()
        # Calculate max memories as a third of the total grid cells
        max_memories = (grid_width * grid_height) // 4
        # Get the current number of memories the person has
        memory_count = len(self._person.get_memories().get_memories())
        # Calculate the priority for 'EXPLORE' using linear scaling from 1 to 10
        explore_priority: int = int(1 + (9 * (memory_count / max_memories)))
        # Ensure the priority is bounded between 1 and 10
        explore_priority = max(1, min(explore_priority, 10))
        # Assign the calculated priority to the 'EXPLORE' task
        self._task_type_priorities[TaskType.EXPLORE] = int(explore_priority)

    def _set_start_construction_task_priorities(self):
        # Define the start construction tasks
        start_construction_tasks = [
            TaskType.START_FARM_CONSTRUCTION,
            TaskType.START_BARN_CONSTRUCTION,
            TaskType.START_MINE_CONSTRUCTION,
            TaskType.START_HOME_CONSTRUCTION
        ]

        # Get the current 'EXPLORE' priority
        explore_priority = self._task_type_priorities[TaskType.EXPLORE]

        # Set the start construction tasks priority relative to explore priority
        if explore_priority >= 5:
            # If explore priority is 5 or higher, make construction tasks lower priority than explore
            construction_priority = 1  # This ensures construction is higher than explore
        else:
            # If explore priority is less than 5, give construction tasks a higher priority
            construction_priority = min(explore_priority + 1, 10)

        # Assign the calculated priority to all start construction tasks
        for task in start_construction_tasks:
            self._task_type_priorities[task] = construction_priority

    def _set_transport_priority(self):
        # Get the current capacity and remaining capacity of the backpack
        backpack_capacity = self._person.get_backpack().get_capacity()
        remaining_capacity = self._person.get_backpack().get_remaining_capacity()
    
        # Calculate how full the backpack is (between 0 and 1)
        fullness_percentage = (backpack_capacity - remaining_capacity) / backpack_capacity
    
        # Calculate the transport priority (between 1 and 10)
        # The fuller the backpack, the higher the transport priority
        transport_priority = 10 - int(10 * fullness_percentage)
        
        # Ensure the priority is between 1 and 10
        transport_priority = max(1, min(transport_priority, 10))
    
        # Assign the calculated priority to the 'TRANSPORT' task
        self._task_type_priorities[TaskType.TRANSPORT] = int(transport_priority)

    def _set_resource_gathering_priorities(self):
        # Retrieve barn locations and capacities
        barn_locations = self._person.get_memories().get_barn_locations()
    
        total_food = 0
        total_wood = 0
        total_stone = 0
        total_capacity = 0
    
        # Iterate through all barns to calculate total food, wood, stone, and capacity
        for barn_location in barn_locations:
            barn = self._person.get_simulation().get_grid().get_structure(barn_location)
    
            if isinstance(barn, Barn): 
                total_food += barn.get_resource("food") 
                total_wood += barn.get_resource("wood")  
                total_stone += barn.get_resource("stone")  
                total_capacity += barn.get_capacity() 
    
        # Calculate the amount of food, wood, and stone relative to the barn's capacity
        food_percentage = total_food / total_capacity if total_capacity > 0 else 0
        wood_percentage = total_wood / total_capacity if total_capacity > 0 else 0
        stone_percentage = total_stone / total_capacity if total_capacity > 0 else 0
    
        # Adjust priorities based on these values
        self._adjust_work_farm_priority(food_percentage)
        self._adjust_chop_wood_priority(wood_percentage)
        self._adjust_work_mine_priority(stone_percentage)
    
    def _adjust_work_farm_priority(self, food_percentage: float):
        self._task_type_priorities[TaskType.WORK_FARM] = max(1, min(10, int(10 * food_percentage)))
    
    def _adjust_chop_wood_priority(self, wood_percentage: float):
        self._task_type_priorities[TaskType.CHOP_TREE] = max(1, min(10, int(10 * wood_percentage)))
    
    def _adjust_work_mine_priority(self, stone_percentage: float):
        self._task_type_priorities[TaskType.WORK_MINE] = max(1, min(10, int(10 * stone_percentage)))

    def _set_barn_construction_priorities(self):
        construction_count = len(self._person.get_memories().get_barn_construction_locations())
        if construction_count == 0:
            self._task_type_priorities[TaskType.BUILD_BARN] = 10
            return 
        self._task_type_priorities[TaskType.BUILD_BARN] = max(1, min(10, 3 - construction_count))
    
    def _set_farm_construction_priorities(self):
        construction_count = len(self._person.get_memories().get_farm_construction_locations())
        if construction_count == 0:
            self._task_type_priorities[TaskType.BUILD_FARM] = 10
            return
        self._task_type_priorities[TaskType.BUILD_FARM] = max(1, min(10, 3 - construction_count))
    
    def _set_home_construction_priorities(self):
        construction_count = len(self._person.get_memories().get_home_construction_locations())
        if construction_count == 0:
            self._task_type_priorities[TaskType.BUILD_HOME] = 10
            return
        self._task_type_priorities[TaskType.BUILD_HOME] = max(1, min(10, 3 - construction_count))
    
    def _set_mine_construction_priorities(self):
        construction_count = len(self._person.get_memories().get_mine_construction_locations())
        if construction_count == 0:
            self._task_type_priorities[TaskType.BUILD_MINE] = 10
            return
        self._task_type_priorities[TaskType.BUILD_MINE] = max(1, min(10, 3 - construction_count))