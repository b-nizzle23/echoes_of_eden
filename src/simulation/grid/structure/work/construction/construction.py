from abc import ABC
from typing import Optional, override
from src.simulation.grid.grid import Grid
from src.simulation.grid.location import Location
from src.simulation.grid.structure.work.work import Work
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
        self._required_wood: int = required_wood  # Total wood required for construction
        self._required_stone: int = (
            required_stone  # Total stone required for construction
        )
        self._delivered_wood: int = 0  # Total wood delivered so far
        self._delivered_stone: int = 0  # Total stone delivered so far
        self._current_completion_level: int = (
            0  # Tracks the current completion progress
        )
        self._finished_completion_level: int = (
            finished_completion_level  # Completion level when construction is finished
        )
        self._max_worker_count: int = max_worker_count
        self._max_work_count: int = (
            max_work_count  # Total work needed to complete the construction
        )

    def deliver_wood(self, amount: int) -> None:
        """
        This method allows the delivery of wood to the construction site.
        The delivery of wood increases the amount of wood on the site.
        """
        self._delivered_wood += amount
        if self._delivered_wood > self._required_wood:
            self._delivered_wood = (
                self._required_wood
            )  # Cap the delivery at the required amount

    def deliver_stone(self, amount: int) -> None:
        """
        This method allows the delivery of stone to the construction site.
        The delivery of stone increases the amount of stone on the site.
        """
        self._delivered_stone += amount
        if self._delivered_stone > self._required_stone:
            self._delivered_stone = (
                self._required_stone
            )  # Cap the delivery at the required amount

    def needs_stone(self) -> bool:
        return self._delivered_stone < self._required_stone

    def needs_wood(self) -> bool:
        return self._delivered_wood < self._required_wood

    def how_much_stone(self) -> int:
        return self._required_stone - self._delivered_stone

    def how_much_wood(self) -> int:
        return self._required_wood - self._delivered_wood

    @override
    def work(self, person: Person) -> Optional[int]:
        """
        Assign a worker to the work, track work progress, and return the yield if max work count is reached.
        """
        if person in self._workers:
            self._workers[person] += 1
        elif len(self._workers) < self._max_worker_count:
            self._workers[person] = 1

        if self._workers[person] > self._max_work_count:
            self.remove_worker(person)
            self._current_completion_level += 1
            return int(
                self._get_yield()
            )  # Return the generated yield amount as an integer.

        return None

    @override
    def work_time_estimate(self) -> int:
        # Estimate time left based on the remaining work to be done
        return (
            self._finished_completion_level - self._current_completion_level
        ) * self._max_work_count

    @override
    def has_capacity(self) -> bool:
        # Construction is "full" when there is no remaining work to be done
        return self._current_completion_level < self._finished_completion_level
