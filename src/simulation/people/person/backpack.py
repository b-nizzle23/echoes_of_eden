from typing import Dict, Optional

from src.settings import settings


class Backpack:
    def __init__(self):
        allowed_resources: Dict[str, int] = {
            settings.get("food", "food"):
                settings.get("backpack_food_store", 100),
            settings.get("stone", "stone"):
                settings.get("backpack_stone_store", 50),
            settings.get("wood", "wood"):
                settings.get("backpack_wood_store", 50),
        }  # Resources and their max capacities
        # Initialize the resources dictionary with allowed resources
        self.resources = {resource: 0 for resource in allowed_resources}
        # Store the max capacity for all resources combined (this is the overall capacity of the store)
        self._capacity = sum(
            allowed_resources.values()
        )  # The total capacity is the sum of the allowed resources' capacities

    def has_capacity(self) -> bool:
        """
        Checks if there is capacity for additional resources in the store.
        This method ensures that the sum of all stored resources does not exceed the store's capacity.
        """
        # Sum the resources stored and check if it is less than the store's total capacity
        total_stored = sum(self.resources.values())
        return total_stored < self._capacity

    def what_resource(self) -> Optional[str]:
        """
        Returns the name of the resource that has the most quantity in the backpack.
        If all resources have 0, returns 'No resources'.
        """
        # Find the resource with the highest quantity
        max_resource = max(self.resources, key=self.resources.get)
        # If all resources have 0, return 'No resources'
        if self.resources[max_resource] == 0:
            return None
        return max_resource

    def add_resource(self, resource: str, amount: int) -> None:
        """
        Adds a resource to the store, respecting the collective capacity limit.
        """
        if resource not in self.resources:
            raise ValueError(f"Resource {resource} is not supported by this store.")

        # Check if adding this resource would exceed the collective capacity
        if self.has_capacity():
            self.resources[resource] += amount
        else:
            raise ValueError("Not enough capacity to add more resources to the store.")

    def remove_resource(self, resource: str, amount: int) -> int:
        """
        Removes a resource from the store, returns the amount removed.
        """
        if resource not in self.resources:
            raise ValueError(f"Resource {resource} is not supported by this store.")

        available = self.resources[resource]
        removed = min(available, amount)
        self.resources[resource] -= removed
        return removed

    def get_resource(self, resource: str) -> int:
        """
        Returns the current amount of a resource stored.
        """
        return self.resources.get(resource, 0)

    def get_remaining_capacity(self) -> int:
        """
        Returns the remaining capacity of the store.
        The remaining capacity is the difference between the total store capacity and the sum of the stored resources.
        """
        total_stored = sum(self.resources.values())
        return self._capacity - total_stored

    def get_capacity(self) -> int:
        """
        Returns the total capacity of the store (sum of all allowed resources' capacities).
        """
        return self._capacity

    def has_items(self) -> bool:
        return self.get_remaining_capacity() != self.get_capacity()
