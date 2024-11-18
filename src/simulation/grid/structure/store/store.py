from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, Dict, override, List
from src.logger import logger
from src.simulation.grid.structure.structure import Structure

if TYPE_CHECKING:
    from src.simulation.grid.grid import Grid
    from src.simulation.grid.location import Location


class Store(Structure, ABC):
    def __init__(
            self,
            grid: Grid,
            location: Location,  # top left corner
            width: int,
            height: int,
            char: str,
            allowed_resources: Dict[str, int],  # Resources and their max capacities
    ):
        logger.debug(f"Initializing Store at location {location}, size ({width}, {height}), character {char}")

        super().__init__(grid, location, width, height, char)

        # Initialize the resources dictionary with allowed resources
        self._resources = {resource: 0 for resource in allowed_resources}

        # Store the max capacity for all resources combined (this is the overall capacity of the store)
        self._capacity = sum(allowed_resources.values())

        logger.debug(f"Store capacity initialized: {self._capacity} (Total of allowed resources' capacities)")

    @override
    def has_capacity(self) -> bool:
        """
        Checks if there is capacity for additional resources in the store.
        This method ensures that the sum of all stored resources does not exceed the store's capacity.
        """
        total_stored = sum(self._resources.values())
        logger.debug(f"Checking capacity: Total stored = {total_stored}, Total capacity = {self._capacity}")
        return total_stored < self._capacity

    @staticmethod
    @override
    def work_time_estimate() -> int:
        """
        Default work time estimate for all stores. Returns 1 by default.
        """
        return 1

    def get_resource_names(self) -> List[str]:
        logger.debug("Fetching resource names from the store.")
        return list(self._resources.keys())

    def add_resource(self, resource: str, amount: int) -> None:
        """
        Adds a resource to the store, respecting the collective capacity limit.
        """
        if resource not in self._resources:
            logger.error(f"Attempted to add unsupported resource: {resource}")
            raise ValueError(f"Resource {resource} is not supported by this store.")

        logger.debug(f"Attempting to add {amount} of {resource} to the store.")

        if self.has_capacity():
            self._resources[resource] += amount
            logger.info(f"Added {amount} of {resource} to the store. Current amount: {self._resources[resource]}")
        else:
            logger.error("Not enough capacity to add more resources.")
            raise ValueError("Not enough capacity to add more resources to the store.")

    def remove_resource(self, resource: str, amount: int) -> int:
        """
        Removes a resource from the store, returns the amount removed.
        """
        if resource not in self._resources:
            logger.error(f"Attempted to remove unsupported resource: {resource}")
            raise ValueError(f"Resource {resource} is not supported by this store.")

        available = self._resources[resource]
        removed = min(available, amount)
        self._resources[resource] -= removed

        logger.info(f"Removed {removed} of {resource} from the store. Remaining: {self._resources[resource]}")
        return removed

    def get_resource(self, resource: str) -> int:
        """
        Returns the current amount of a resource stored.
        """
        amount = self._resources.get(resource, 0)
        logger.debug(f"Retrieved {amount} of {resource} from the store.")
        return amount

    def get_remaining_capacity(self) -> int:
        """
        Returns the remaining capacity of the store.
        The remaining capacity is the difference between the total store capacity and the sum of the stored resources.
        """
        total_stored = sum(self._resources.values())
        remaining_capacity = self._capacity - total_stored
        logger.debug(f"Remaining capacity: {remaining_capacity}")
        return remaining_capacity

    def get_capacity(self) -> int:
        """
        Returns the total capacity of the store (sum of all allowed resources' capacities).
        """
        logger.debug(f"Store total capacity: {self._capacity}")
        return self._capacity
