from src.simulation.grid.structure.structure_factory import logger
from src.simulation.people.people import People
from src.simulation.people.person.scheduler.task.construction.build_barn import \
    BuildBarn
from src.simulation.people.person.scheduler.task.construction.build_farm import \
    BuildFarm
from src.simulation.people.person.scheduler.task.construction.build_home import \
    BuildHome
from src.simulation.people.person.scheduler.task.construction.build_mine import \
    BuildMine
from src.simulation.people.person.scheduler.task.eat import Eat
from src.simulation.people.person.scheduler.task.explore import Explore
from src.simulation.people.person.scheduler.task.find_home import FindHome
from src.simulation.people.person.scheduler.task.find_spouse import FindSpouse
from src.simulation.people.person.scheduler.task.start_construction.start_barn_construction import \
    StartBarnConstruction
from src.simulation.people.person.scheduler.task.start_construction.start_farm_construction import \
    StartFarmConstruction
from src.simulation.people.person.scheduler.task.start_construction.start_home_construction import \
    StartHomeConstruction
from src.simulation.people.person.scheduler.task.start_construction.start_mine_construction import \
    StartMineConstruction
from src.simulation.people.person.scheduler.task.transport import Transport
from src.simulation.people.person.scheduler.task.work.chop_tree import ChopTree
from src.simulation.people.person.scheduler.task.work.work_farm import WorkFarm
from src.simulation.people.person.scheduler.task.work.work_mine import WorkMine
from src.simulation.visualization.state.state import State


class TaskState(State):
    def __init__(self, people: People):
        logger.debug("Initializing task statistics object.")
        self._people = people

        # Log start of average calculations
        logger.debug("Calculating average task counts.")

        self._average_complete_task_count: float = self._get_average_complete_task_count()
        logger.debug(f"Average complete task count: {self._average_complete_task_count}")

        self._average_active_task_count: float = self._get_average_active_task_count()
        logger.debug(f"Average active task count: {self._average_active_task_count}")

        self._average_active_build_barn_task_count: float = self._get_average_active_build_barn_task_count()
        logger.debug(f"Average active build barn task count: {self._average_active_build_barn_task_count}")

        self._average_complete_build_barn_task_count: float = self._get_average_complete_build_barn_task_count()
        logger.debug(f"Average complete build barn task count: {self._average_complete_build_barn_task_count}")

        self._average_active_build_farm_task_count: float = self._get_average_active_build_farm_task_count()
        logger.debug(f"Average active build farm task count: {self._average_active_build_farm_task_count}")

        self._average_complete_build_farm_task_count: float = self._get_average_complete_build_farm_task_count()
        logger.debug(f"Average complete build farm task count: {self._average_complete_build_farm_task_count}")

        self._average_active_build_home_task_count: float = self._get_average_active_build_home_task_count()
        logger.debug(f"Average active build home task count: {self._average_active_build_home_task_count}")

        self._average_complete_build_home_task_count: float = self._get_average_complete_build_home_task_count()
        logger.debug(f"Average complete build home task count: {self._average_complete_build_home_task_count}")

        self._average_active_build_mine_task_count: float = self._get_average_active_build_mine_task_count()
        logger.debug(f"Average active build mine task count: {self._average_active_build_mine_task_count}")

        self._average_complete_build_mine_task_count: float = self._get_average_complete_build_mine_task_count()
        logger.debug(f"Average complete build mine task count: {self._average_complete_build_mine_task_count}")

        self._average_active_chop_tree_task_count: float = self._get_average_active_chop_tree_task_count()
        logger.debug(f"Average active chop tree task count: {self._average_active_chop_tree_task_count}")

        self._average_complete_chop_tree_task_count: float = self._get_average_complete_chop_tree_task_count()
        logger.debug(f"Average complete chop tree task count: {self._average_complete_chop_tree_task_count}")

        self._average_active_eat_task_count: float = self._get_average_active_eat_task_count()
        logger.debug(f"Average active eat task count: {self._average_active_eat_task_count}")

        self._average_complete_eat_task_count: float = self._get_average_complete_eat_task_count()
        logger.debug(f"Average complete eat task count: {self._average_complete_eat_task_count}")

        self._average_active_explore_task_count: float = self._get_average_active_explore_task_count()
        logger.debug(f"Average active explore task count: {self._average_active_explore_task_count}")

        self._average_complete_explore_task_count: float = self._get_average_complete_explore_task_count()
        logger.debug(f"Average complete explore task count: {self._average_complete_explore_task_count}")

        self._average_active_find_home_task_count: float = self._get_average_active_find_home_task_count()
        logger.debug(f"Average active find home task count: {self._average_active_find_home_task_count}")

        self._average_complete_find_home_task_count: float = self._get_average_complete_find_home_task_count()
        logger.debug(f"Average complete find home task count: {self._average_complete_find_home_task_count}")

        self._average_active_find_spouse_task_count: float = self._get_average_active_find_spouse_task_count()
        logger.debug(f"Average active find spouse task count: {self._average_active_find_spouse_task_count}")

        self._average_complete_find_spouse_task_count: float = self._get_average_complete_find_spouse_task_count()
        logger.debug(f"Average complete find spouse task count: {self._average_complete_find_spouse_task_count}")

        self._average_active_start_barn_construction_task_count: float = self._get_average_active_start_barn_construction_task_count()
        logger.debug(
            f"Average active start barn construction task count: {self._average_active_start_barn_construction_task_count}")

        self._average_complete_start_barn_construction_task_count: float = self._get_average_complete_start_barn_construction_task_count()
        logger.debug(
            f"Average complete start barn construction task count: {self._average_complete_start_barn_construction_task_count}")

        self._average_active_start_farm_construction_task_count: float = self._get_average_active_start_farm_construction_task_count()
        logger.debug(
            f"Average active start farm construction task count: {self._average_active_start_farm_construction_task_count}")

        self._average_complete_start_farm_construction_task_count: float = self._get_average_complete_start_farm_construction_task_count()
        logger.debug(
            f"Average complete start farm construction task count: {self._average_complete_start_farm_construction_task_count}")

        self._average_active_start_home_construction_task_count: float = self._get_average_active_start_home_construction_task_count()
        logger.debug(
            f"Average active start home construction task count: {self._average_active_start_home_construction_task_count}")

        self._average_complete_start_home_construction_task_count: float = self._get_average_complete_start_home_construction_task_count()
        logger.debug(
            f"Average complete start home construction task count: {self._average_complete_start_home_construction_task_count}")

        self._average_active_start_mine_construction_task_count: float = self._get_average_active_start_mine_construction_task_count()
        logger.debug(
            f"Average active start mine construction task count: {self._average_active_start_mine_construction_task_count}")

        self._average_complete_start_mine_construction_task_count: float = self._get_average_complete_start_mine_construction_task_count()
        logger.debug(
            f"Average complete start mine construction task count: {self._average_complete_start_mine_construction_task_count}")

        self._average_active_work_farm_task_count: float = self._get_average_active_work_farm_task_count()
        logger.debug(f"Average active work farm task count: {self._average_active_work_farm_task_count}")

        self._average_complete_work_farm_task_count: float = self._get_average_complete_work_farm_task_count()
        logger.debug(f"Average complete work farm task count: {self._average_complete_work_farm_task_count}")

        self._average_active_work_mine_task_count: float = self._get_average_active_work_mine_task_count()
        logger.debug(f"Average active work mine task count: {self._average_active_work_mine_task_count}")

        self._average_complete_work_mine_task_count: float = self._get_average_complete_work_mine_task_count()
        logger.debug(f"Average complete work mine task count: {self._average_complete_work_mine_task_count}")

        self._average_active_transport_task_count: float = self._get_average_active_transport_task_count()
        logger.debug(f"Average active transport task count: {self._average_active_transport_task_count}")

        self._average_complete_transport_task_count: float = self._get_average_complete_transport_task_count()
        logger.debug(f"Average complete transport task count: {self._average_complete_transport_task_count}")

        # Log cleanup
        logger.debug("Cleaning up by deleting people object.")
        del self._people
        logger.debug("Task statistics object initialization completed.")

    def _get_average_task_count_with_predicate(self, task_predicate: callable) -> float:
        logger.debug("Calculating average task count with predicate.")
        total_count = 0.0
        for person in self._people:
            count = sum(1 for task in person.get_scheduler().get_this_years_tasks() if task_predicate(task))
            logger.debug(f"Person {person} has {count} tasks matching the predicate.")
            total_count += count
        average = total_count / len(self._people) if self._people else 0.0
        logger.debug(
            f"Total matching tasks: {total_count}. Number of people: {len(self._people) if self._people else 0}. Average: {average}."
        )
        return average

    def _get_average_complete_task_count(self) -> float:
        logger.debug("Calculating average complete task count.")
        average = self._get_average_task_count_with_predicate(lambda task: task.is_finished())
        logger.debug(f"Average complete task count: {average}")
        return average

    def _get_average_active_task_count(self) -> float:
        logger.debug("Calculating average active task count.")
        average = self._get_average_task_count_with_predicate(lambda task: not task.is_finished())
        logger.debug(f"Average active task count: {average}")
        return average

    def _get_average_active_build_barn_task_count(self) -> float:
        logger.debug("Calculating average active build barn task count.")
        average = self._get_average_task_count_with_predicate(
            lambda task: isinstance(task, BuildBarn) and not task.is_finished()
        )
        logger.debug(f"Average active build barn task count: {average}")
        return average

    def _get_average_complete_build_barn_task_count(self) -> float:
        logger.debug("Calculating average complete build barn task count.")
        average = self._get_average_task_count_with_predicate(
            lambda task: isinstance(task, BuildBarn) and task.is_finished()
        )
        logger.debug(f"Average complete build barn task count: {average}")
        return average

    def _get_average_active_build_farm_task_count(self) -> float:
        logger.debug("Calculating average active build farm task count.")
        average = self._get_average_task_count_with_predicate(
            lambda task: isinstance(task, BuildFarm) and not task.is_finished()
        )
        logger.debug(f"Average active build farm task count: {average}")
        return average

    def _get_average_complete_build_farm_task_count(self) -> float:
        logger.debug("Calculating average complete build farm task count.")
        average = self._get_average_task_count_with_predicate(
            lambda task: isinstance(task, BuildFarm) and task.is_finished()
        )
        logger.debug(f"Average complete build farm task count: {average}")
        return average

    def _get_average_active_build_home_task_count(self) -> float:
        logger.debug("Calculating average active build home task count.")
        average = self._get_average_task_count_with_predicate(
            lambda task: isinstance(task, BuildHome) and not task.is_finished()
        )
        logger.debug(f"Average active build home task count: {average}")
        return average

    def _get_average_complete_build_home_task_count(self) -> float:
        logger.debug("Calculating average complete build home task count.")
        average = self._get_average_task_count_with_predicate(
            lambda task: isinstance(task, BuildHome) and task.is_finished()
        )
        logger.debug(f"Average complete build home task count: {average}")
        return average

    def _get_average_active_build_mine_task_count(self) -> float:
        logger.debug("Calculating average active build mine task count.")
        average = self._get_average_task_count_with_predicate(
            lambda task: isinstance(task, BuildMine) and not task.is_finished()
        )
        logger.debug(f"Average active build mine task count: {average}")
        return average

    def _get_average_complete_build_mine_task_count(self) -> float:
        logger.debug("Calculating average complete build mine task count.")
        average = self._get_average_task_count_with_predicate(
            lambda task: isinstance(task, BuildMine) and task.is_finished()
        )
        logger.debug(f"Average complete build mine task count: {average}")
        return average

    def _get_average_active_chop_tree_task_count(self) -> float:
        logger.debug("Calculating average active chop tree task count.")
        average = self._get_average_task_count_with_predicate(
            lambda task: isinstance(task, ChopTree) and not task.is_finished()
        )
        logger.debug(f"Average active chop tree task count: {average}")
        return average

    def _get_average_complete_chop_tree_task_count(self) -> float:
        logger.debug("Calculating average complete chop tree task count.")
        average = self._get_average_task_count_with_predicate(
            lambda task: isinstance(task, ChopTree) and task.is_finished()
        )
        logger.debug(f"Average complete chop tree task count: {average}")
        return average

    def _get_average_active_eat_task_count(self) -> float:
        logger.debug("Calculating average active eat task count.")
        average = self._get_average_task_count_with_predicate(
            lambda task: isinstance(task, Eat) and not task.is_finished()
        )
        logger.debug(f"Average active eat task count: {average}")
        return average

    def _get_average_complete_eat_task_count(self) -> float:
        logger.debug("Calculating average complete eat task count.")
        average = self._get_average_task_count_with_predicate(
            lambda task: isinstance(task, Eat) and task.is_finished()
        )
        logger.debug(f"Average complete eat task count: {average}")
        return average

    def _get_average_active_explore_task_count(self) -> float:
        logger.debug("Calculating average active explore task count.")
        average = self._get_average_task_count_with_predicate(
            lambda task: isinstance(task, Explore) and not task.is_finished()
        )
        logger.debug(f"Average active explore task count: {average}")
        return average

    def _get_average_complete_explore_task_count(self) -> float:
        logger.debug("Calculating average complete explore task count.")
        average = self._get_average_task_count_with_predicate(
            lambda task: isinstance(task, Explore) and task.is_finished()
        )
        logger.debug(f"Average complete explore task count: {average}")
        return average

    def _get_average_active_find_home_task_count(self) -> float:
        logger.debug("Calculating average active find home task count.")
        average = self._get_average_task_count_with_predicate(
            lambda task: isinstance(task, FindHome) and not task.is_finished()
        )
        logger.debug(f"Average active find home task count: {average}")
        return average

    def _get_average_complete_find_home_task_count(self) -> float:
        logger.debug("Calculating average complete find home task count.")
        average = self._get_average_task_count_with_predicate(
            lambda task: isinstance(task, FindHome) and task.is_finished()
        )
        logger.debug(f"Average complete find home task count: {average}")
        return average

    def _get_average_active_find_spouse_task_count(self) -> float:
        logger.debug("Calculating average active find spouse task count.")
        average = self._get_average_task_count_with_predicate(
            lambda task: isinstance(task, FindSpouse) and not task.is_finished()
        )
        logger.debug(f"Average active find spouse task count: {average}")
        return average

    def _get_average_complete_find_spouse_task_count(self) -> float:
        logger.debug("Calculating average complete find spouse task count.")
        average = self._get_average_task_count_with_predicate(
            lambda task: isinstance(task, FindSpouse) and task.is_finished()
        )
        logger.debug(f"Average complete find spouse task count: {average}")
        return average

    def _get_average_active_start_barn_construction_task_count(self) -> float:
        logger.debug("Calculating average active start barn construction task count.")
        average = self._get_average_task_count_with_predicate(
            lambda task: isinstance(task, StartBarnConstruction) and not task.is_finished()
        )
        logger.debug(f"Average active start barn construction task count: {average}")
        return average

    def _get_average_complete_start_barn_construction_task_count(self) -> float:
        logger.debug("Calculating average complete start barn construction task count.")
        average = self._get_average_task_count_with_predicate(
            lambda task: isinstance(task, StartBarnConstruction) and task.is_finished()
        )
        logger.debug(f"Average complete start barn construction task count: {average}")
        return average

    def _get_average_active_start_farm_construction_task_count(self) -> float:
        logger.debug("Calculating average active start farm construction task count.")
        average = self._get_average_task_count_with_predicate(
            lambda task: isinstance(task, StartFarmConstruction) and not task.is_finished()
        )
        logger.debug(f"Average active start farm construction task count: {average}")
        return average

    def _get_average_complete_start_farm_construction_task_count(self) -> float:
        logger.debug("Calculating average complete start farm construction task count.")
        average = self._get_average_task_count_with_predicate(
            lambda task: isinstance(task, StartFarmConstruction) and task.is_finished()
        )
        logger.debug(f"Average complete start farm construction task count: {average}")
        return average

    def _get_average_active_start_home_construction_task_count(self) -> float:
        logger.debug("Calculating average active start home construction task count.")
        average = self._get_average_task_count_with_predicate(
            lambda task: isinstance(task, StartHomeConstruction) and not task.is_finished()
        )
        logger.debug(f"Average active start home construction task count: {average}")
        return average

    def _get_average_complete_start_home_construction_task_count(self) -> float:
        logger.debug("Calculating average complete start home construction task count.")
        average = self._get_average_task_count_with_predicate(
            lambda task: isinstance(task, StartHomeConstruction) and task.is_finished()
        )
        logger.debug(f"Average complete start home construction task count: {average}")
        return average

    def _get_average_active_start_mine_construction_task_count(self) -> float:
        logger.debug("Calculating average active start mine construction task count.")
        average = self._get_average_task_count_with_predicate(
            lambda task: isinstance(task, StartMineConstruction) and not task.is_finished()
        )
        logger.debug(f"Average active start mine construction task count: {average}")
        return average

    def _get_average_complete_start_mine_construction_task_count(self) -> float:
        logger.debug("Calculating average complete start mine construction task count.")
        average = self._get_average_task_count_with_predicate(
            lambda task: isinstance(task, StartMineConstruction) and task.is_finished()
        )
        logger.debug(f"Average complete start mine construction task count: {average}")
        return average

    def _get_average_active_work_farm_task_count(self) -> float:
        logger.debug("Calculating average active work farm task count.")
        average = self._get_average_task_count_with_predicate(
            lambda task: isinstance(task, WorkFarm) and not task.is_finished()
        )
        logger.debug(f"Average active work farm task count: {average}")
        return average

    def _get_average_complete_work_farm_task_count(self) -> float:
        logger.debug("Calculating average complete work farm task count.")
        average = self._get_average_task_count_with_predicate(
            lambda task: isinstance(task, WorkFarm) and task.is_finished()
        )
        logger.debug(f"Average complete work farm task count: {average}")
        return average

    def _get_average_active_work_mine_task_count(self) -> float:
        logger.debug("Calculating average active work mine task count.")
        average = self._get_average_task_count_with_predicate(
            lambda task: isinstance(task, WorkMine) and not task.is_finished()
        )
        logger.debug(f"Average active work mine task count: {average}")
        return average

    def _get_average_complete_work_mine_task_count(self) -> float:
        logger.debug("Calculating average complete work mine task count.")
        average = self._get_average_task_count_with_predicate(
            lambda task: isinstance(task, WorkMine) and task.is_finished()
        )
        logger.debug(f"Average complete work mine task count: {average}")
        return average

    def _get_average_active_transport_task_count(self) -> float:
        logger.debug("Calculating average active transport task count.")
        average = self._get_average_task_count_with_predicate(
            lambda task: isinstance(task, Transport) and not task.is_finished()
        )
        logger.debug(f"Average active transport task count: {average}")
        return average

    def _get_average_complete_transport_task_count(self) -> float:
        logger.debug("Calculating average complete transport task count.")
        average = self._get_average_task_count_with_predicate(
            lambda task: isinstance(task, Transport) and task.is_finished()
        )
        logger.debug(f"Average complete transport task count: {average}")
        return average

