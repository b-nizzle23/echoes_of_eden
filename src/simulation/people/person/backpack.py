from typing import Dict, Optional

from src.settings import settings
from src.logger import logger


class Backpack:
    def __init__(self):
        logger.info("Initializing Backpack with allowed resources and capacities.")
        allowed_resources: Dict[str, int] = {
            settings.get("food", "food"): settings.get("backpack_food_store", 100),
            settings.get("stone", "stone"): settings.get("backpack_stone_store", 50),
            settings.get("wood", "wood"): settings.get("backpack_wood_store", 50),
        }  # Resources and their max capacities
        # Initialize the resources dictionary with allowed resources
        self.resources = {resource: 0 for resource in allowed_resources}
        # Store the max capacity for all resources combined (this is the overall capacity of the store)
        self._capacity = sum(
            allowed_resources.values()
        )  # The total capacity is the sum of the allowed resources' capacities
        logger.debug(
            "Backpack initialized with resources: %s and total capacity: %d.",
            self.resources,
            self._capacity,
        )

    def has_capacity(self) -> bool:
        """
        Checks if there is capacity for additional resources in the store.
        This method ensures that the sum of all stored resources does not exceed the store's capacity.
        """
        # Sum the resources stored and check if it is less than the store's total capacity
        total_stored = sum(self.resources.values())
        logger.info("Checking if backpack has capacity.")
        logger.debug(
            "Current total stored: %d, Total capacity: %d.", total_stored, self._capacity
        )
        return total_stored < self._capacity

    def what_resource(self) -> Optional[str]:
        """
        Returns the name of the resource that has the most quantity in the backpack.
        If all resources have 0, returns 'No resources'.
        """
        logger.info("Determining the resource with the highest quantity in the backpack.")
        if not self.has_items():
            logger.debug("Backpack is empty; no resource to return.")
            return None

        # Find the resource with the highest quantity
        max_resource = max(self.resources, key=self.resources.get)
        logger.debug("Resource with highest quantity: %s.", max_resource)

        # If all resources have 0, return 'No resources'
        if self.resources[max_resource] == 0:
            return None
        return max_resource

    def add_resource(self, resource: str, amount: int) -> None:
        """
        Adds a resource to the store, respecting the collective capacity limit.
        """
        logger.info("Adding resource %s with amount %d.", resource, amount)

        if resource not in self.resources:
            logger.error("Attempted to add unsupported resource: %s.", resource)
            raise ValueError(f"Resource {resource} is not supported by this store.")

        # Check if adding this resource would exceed the collective capacity
        if self.has_capacity():
            logger.debug("Adding %d of %s to the backpack.", amount, resource)
            self.resources[resource] += amount
        else:
            logger.warning("Not enough capacity to add %d of %s.", amount, resource)
            raise ValueError("Not enough capacity to add more resources to the store.")

    def remove_resource(self, resource: str, amount: int) -> int:
        """
        Removes a resource from the store, returns the amount removed.
        """
        logger.info("Removing %d of %s from the backpack.", amount, resource)

        if resource not in self.resources:
            logger.error("Attempted to remove unsupported resource: %s.", resource)
            raise ValueError(f"Resource {resource} is not supported by this store.")

        available = self.resources[resource]
        removed = min(available, amount)
        self.resources[resource] -= removed
        logger.debug(
            "Removed %d of %s from the backpack. Remaining: %d.",
            removed,
            resource,
            self.resources[resource],
        )
        return removed

    def get_resource(self, resource: str) -> int:
        """
        Returns the current amount of a resource stored.
        """
        logger.info("Fetching the quantity of resource: %s.", resource)
        if resource not in self.resources:
            logger.warning("Resource %s is not stored in the backpack.", resource)
            return 0
        logger.debug(
            "Current amount of %s in the backpack: %d.", resource, self.resources[resource]
        )
        return self.resources[resource]

    def get_remaining_capacity(self) -> int:
        """
        Returns the remaining capacity of the store.
        The remaining capacity is the difference between the total store capacity and the sum of the stored resources.
        """
        logger.info("Calculating remaining capacity of the backpack.")
        total_stored = sum(self.resources.values())
        remaining_capacity = self._capacity - total_stored
        logger.debug(
            "Total stored: %d, Remaining capacity: %d.", total_stored, remaining_capacity
        )
        return remaining_capacity

    def get_capacity(self) -> int:
        """
        Returns the total capacity of the store (sum of all allowed resources' capacities).
        """
        return self._capacity

    def has_items(self) -> bool:
        logger.info("Checking if the backpack contains any items.")
        has_items = self.get_remaining_capacity() != self.get_capacity()
        logger.debug("Backpack has items: %s.", has_items)
        return has_items
