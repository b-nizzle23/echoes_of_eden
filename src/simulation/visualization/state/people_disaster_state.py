from typing import Dict

from src.simulation.grid.structure.structure_factory import logger
from src.simulation.people.people import People
from src.simulation.visualization.state.state import State


class PeopleDisasterState(State):
    def __init__(self, people: People):
        # Get disaster counts from the PeopleDisasterGenerator
        disaster_counts: Dict[str, int] = people.get_disaster_counts()

        # Initialize disaster attributes based on counts
        self._divorce = disaster_counts.get("divorce", 0)
        logger.debug(f"Divorce disaster count: {self._divorce}")

        self._sickness = disaster_counts.get("sickness", 0)
        logger.debug(f"Sickness disaster count: {self._sickness}")

        self._craving = disaster_counts.get("craving", 0)
        logger.debug(f"Craving disaster count: {self._craving}")

        self._death = disaster_counts.get("death", 0)
        logger.debug(f"Death disaster count: {self._death}")

        self._forget_tasks = disaster_counts.get("forget_tasks", 0)
        logger.debug(f"Forget tasks disaster count: {self._forget_tasks}")

        self._sleepwalk = disaster_counts.get("sleepwalk", 0)
        logger.debug(f"Sleepwalk disaster count: {self._sleepwalk}")

        self._so_many_babies = disaster_counts.get("so_many_babies", 0)
        logger.debug(f"So many babies disaster count: {self._so_many_babies}")
