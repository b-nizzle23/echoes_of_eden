from __future__ import annotations

import itertools
from abc import ABC
from typing import TYPE_CHECKING, Dict, Optional, List, Tuple, Callable
from src.simulation.grid.structure.structure import Structure
from src.logger import logger

if TYPE_CHECKING:
    from src.simulation.grid.grid import Grid
    from src.simulation.grid.location import Location
    from src.simulation.people.person.person import Person


class Work(Structure, ABC):
    def __init__(
        self,
        grid: Grid,
        location: Location,  # top left corner
        width: int,
        height: int,
        char: str,
        max_worker_count: int,
        max_work_count: int,
        yield_func: Callable[[], float],
        yield_variance: float
    ):
        logger.debug(f"Initializing Work at location {location}, size: {width}x{height}")

        super().__init__(grid, location, width, height, char)
        self._max_worker_count = max_worker_count
        self._max_work_count = max_work_count
        self._workers: Dict[Person, int] = {}
        self._yield_func: Callable[[], float] = yield_func
        self._yield_variance: float = yield_variance
        self._decrease_yield_time: int = 0

        logger.info(f"Work initialized with max workers: {max_worker_count}, "
                    f"max work count: {max_work_count}, "
                    f"yield variance: {yield_variance:.2f}")

    def set_yield_func(self, yield_func: Callable[[], float]):
        self._yield_func = yield_func
        logger.debug(f"Yield function set to: {yield_func}")

    def get_yield_func(self) -> Callable[[], float]:
        logger.debug(f"Getting yield function: {self._yield_func}")
        return self._yield_func

    def decrease_yield(self) -> None:
        self._decrease_yield_time = self._grid.get_time()
        logger.debug(f"Yield decreased at time {self._decrease_yield_time}")

    def has_capacity(self) -> bool:
        """
        Check if there is capacity for more workers.
        """
        capacity = len(self._workers) < self._max_worker_count
        logger.debug(f"Checking capacity: {capacity} (current workers: {len(self._workers)}, max workers: {self._max_worker_count})")
        return capacity

    def work_time_estimate(self) -> int:
        """
        Returns the work time estimate for this type of work.
        """
        logger.debug(f"Work time estimate: {self._max_work_count}")
        return self._max_work_count

    def work(self, person: Person) -> Optional[int]:
        """
        Assign a worker to the work, track work progress, and return the yield if max work count is reached.
        """
        logger.debug(f"Assigning worker {person} to work")

        if person in self._workers:
            self._workers[person] += 1
            logger.debug(f"Worker {person} already working, increasing count to {self._workers[person]}")
        elif len(self._workers) < self._max_worker_count:
            self._workers[person] = 1
            logger.debug(f"Worker {person} added to work site")

        if self._workers[person] > self._max_work_count:
            self.remove_worker(person)
            y: int = int(self._get_yield())
            if self._decrease_yield_time != 0 and self._grid.get_time() - self._decrease_yield_time > 50:
                y = y // 2
                logger.debug(f"Yield decreased due to time passed since last decrease. Yield halved: {y}")
            self._decrease_yield_time = 0
            logger.info(f"Work complete for {person}, yield: {y}")
            return y

        return None

    def remove_worker(self, person: Person) -> None:
        """
        Remove a worker from the work site.
        """
        if person in self._workers:
            del self._workers[person]
            logger.debug(f"Worker {person} removed from work site")

    def _get_yield(self) -> float:
        """
        Each subclass should define how to generate the yield, if needed.
        """
        yield_value = self._yield_func() + self._yield_variance
        logger.debug(f"Calculated yield: {yield_value}")
        return yield_value

    def exchange_worker_memories(self):
        workers: List[Person] = list(self._workers.keys())
        pairs: List[Tuple[Person, Person]] = list(itertools.combinations(workers, 2))
        logger.debug(f"Exchanging memories between workers: {workers}")
        for pair in pairs:
            pair[0].exchange_memories(pair[1])
