from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, Optional, override
from src.logger import logger

from src.simulation.grid.structure.work.work import Work

if TYPE_CHECKING:
    from src.simulation.grid.grid import Grid
    from src.simulation.grid.location import Location
    from src.simulation.people.person.person import Person


class Construction(Work, ABC):
    def __init__(
        self,
        grid: Grid,
        location: Location,  # top left corner
        width: int,
        height: int,
        char: str,
        required_wood: int,
        required_stone: int,
        max_work_count: int,  # Max amount of work needed to complete construction
        max_worker_count: int,  # Max number of workers for this construction type
        finished_completion_level: int,  # Target completion level for this construction
    ):
        yield_func = lambda: 1
        yield_variance = 0
        super().__init__(
            grid,
            location,
            width,
            height,
            char,
            max_worker_count,
            max_work_count,
            yield_func,
            yield_variance
        )
        self._required_wood: int = required_wood
        self._required_stone: int = required_stone
        self._delivered_wood: int = 0
        self._delivered_stone: int = 0
        self._current_completion_level: int = 0
        self._finished_completion_level: int = finished_completion_level
        self._max_worker_count: int = max_worker_count
        self._max_work_count: int = max_work_count
        logger.debug(f"Construction initialized with required wood: {required_wood}, required stone: {required_stone}, max work count: {max_work_count}")

    def deliver_wood(self, amount: int) -> None:
        self._delivered_wood += amount
        if self._delivered_wood > self._required_wood:
            self._delivered_wood = self._required_wood
        logger.info(f"Delivered {amount} wood. Total wood delivered: {self._delivered_wood}/{self._required_wood}")

    def deliver_stone(self, amount: int) -> None:
        self._delivered_stone += amount
        if self._delivered_stone > self._required_stone:
            self._delivered_stone = self._required_stone
        logger.info(f"Delivered {amount} stone. Total stone delivered: {self._delivered_stone}/{self._required_stone}")

    def needs_stone(self) -> bool:
        needs = self._delivered_stone < self._required_stone
        logger.debug(f"Needs stone: {needs}")
        return needs

    def needs_wood(self) -> bool:
        needs = self._delivered_wood < self._required_wood
        logger.debug(f"Needs wood: {needs}")
        return needs

    def how_much_stone(self) -> int:
        remaining_stone = self._required_stone - self._delivered_stone
        logger.debug(f"How much stone needed: {remaining_stone}")
        return remaining_stone

    def how_much_wood(self) -> int:
        remaining_wood = self._required_wood - self._delivered_wood
        logger.debug(f"How much wood needed: {remaining_wood}")
        return remaining_wood

    @override
    def work(self, person: Person) -> Optional[int]:
        if person in self._workers:
            self._workers[person] += 1
        elif len(self._workers) < self._max_worker_count:
            self._workers[person] = 1

        if self._workers[person] > self._max_work_count:
            self.remove_worker(person)
            self._current_completion_level += 1
            logger.info(f"Worker {person} finished work. Current completion level: {self._current_completion_level}/{self._finished_completion_level}")
            return int(self._get_yield())

        logger.debug(f"Worker {person} assigned. Current completion level: {self._current_completion_level}/{self._finished_completion_level}")
        return None

    @override
    def work_time_estimate(self) -> int:
        time_left = (self._finished_completion_level - self._current_completion_level) * self._max_work_count
        logger.debug(f"Work time estimate: {time_left}")
        return time_left

    @override
    def has_capacity(self) -> bool:
        capacity = self._current_completion_level < self._finished_completion_level
        logger.debug(f"Has capacity: {capacity}")
        return capacity
