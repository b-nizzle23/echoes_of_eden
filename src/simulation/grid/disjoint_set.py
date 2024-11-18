from typing import List
from src.logger import logger

class DisjointSet:
    def __init__(self, size: int) -> None:
        logger.debug(f"Initializing DisjointSet with size {size}.")
        self.parent: List[int] = list(range(size))
        self.rank: List[int] = [0] * size  # Rank is used for balancing
        logger.debug(f"Parent list initialized: {self.parent}")
        logger.debug(f"Rank list initialized: {self.rank}")

    def find(self, x: int) -> int:
        logger.debug(f"Find operation for element {x}.")
        if self.parent[x] != x:
            logger.debug(f"Element {x} is not a root. Performing path compression.")
            self.parent[x] = self.find(self.parent[x])  # Path compression
        logger.debug(f"Root of element {x} is {self.parent[x]}.")
        return self.parent[x]

    def union(self, x: int, y: int) -> None:
        logger.debug(f"Union operation for elements {x} and {y}.")
        rootX = self.find(x)
        rootY = self.find(y)

        if rootX != rootY:
            # Union by rank: Attach the smaller tree under the larger tree
            if self.rank[rootX] > self.rank[rootY]:
                self.parent[rootY] = rootX
                logger.debug(f"Attaching tree with root {rootY} under tree with root {rootX}.")
            elif self.rank[rootX] < self.rank[rootY]:
                self.parent[rootX] = rootY
                logger.debug(f"Attaching tree with root {rootX} under tree with root {rootY}.")
            else:
                self.parent[rootY] = rootX
                self.rank[rootX] += 1
                logger.debug(f"Attaching tree with root {rootY} under tree with root {rootX} and increasing rank of root {rootX} to {self.rank[rootX]}.")
        else:
            logger.debug(f"Elements {x} and {y} are already in the same set. No union performed.")
