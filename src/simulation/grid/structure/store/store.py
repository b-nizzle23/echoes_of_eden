from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, Dict, override, List

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
        super().__init__(grid, location, width, height, char)

        # Initialize the resources dictionary with allowed resources
        self._resources = {resource: 0 for resource in allowed_resources}
        # Store the max capacity for all resources combined (this is the overall capacity of the store)
        self._capacity = sum(
            allowed_resources.values()
        )  # The total capacity is the sum of the allowed resources' capacities

    @override
    def has_capacity(self) -> bool:
        """
        Checks if there is capacity for additional resources in the store.
        This method ensures that the sum of all stored resources does not exceed the store's capacity.
        """
        # Sum the resources stored and check if it is less than the store's total capacity
        total_stored = sum(self._resources.values())
        return total_stored < self._capacity

    @staticmethod
    @override
    def work_time_estimate() -> int:
        """
        Default work time estimate for all stores. Returns 1 by default.
        """
        return 1

    def get_resource_names(self) -> List[str]:
        return list(self._resources.keys())

    def add_resource(self, resource: str, amount: int) -> None:
        """
        Adds a resource to the store, respecting the collective capacity limit.
        """
        if resource not in self._resources:
            raise ValueError(f"Resource {resource} is not supported by this store.")

        # Check if adding this resource would exceed the collective capacity
        if self.has_capacity():
            self._resources[resource] += amount
        else:
            raise ValueError("Not enough capacity to add more resources to the store.")

    def remove_resource(self, resource: str, amount: int) -> int:
        """
        Removes a resource from the store, returns the amount removed.
        """
        if resource not in self._resources:
            raise ValueError(f"Resource {resource} is not supported by this store.")

        available = self._resources[resource]
        removed = min(available, amount)
        self._resources[resource] -= removed
        return removed

    def get_resource(self, resource: str) -> int:
        """
        Returns the current amount of a resource stored.
        """
        return self._resources.get(resource, 0)

    def get_remaining_capacity(self) -> int:
        """
        Returns the remaining capacity of the store.
        The remaining capacity is the difference between the total store capacity and the sum of the stored resources.
        """
        total_stored = sum(self._resources.values())
        return self._capacity - total_stored

    def get_capacity(self) -> int:
        """
        Returns the total capacity of the store (sum of all allowed resources' capacities).
        """
        return self._capacity
