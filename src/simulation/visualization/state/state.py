import re
from abc import ABC
from numbers import Number
from typing import Dict, Tuple

from src.simulation.grid.structure.structure_factory import logger


class State(ABC):
    def get_data(self) -> Tuple[str, Dict[str, Number]]:
        """
        Returns the data dictionary with labels formatted and mapped to their corresponding values.
        Subclasses should implement this method to specify the class-specific title and attributes.
        """
        logger.debug(f"Getting data for state: {self.__class__.__name__}")
        title = self.get_title()  # Get the title dynamically using each subclass's title
        logger.debug(f"Title obtained: {title}")

        data = self._data_generator()  # Use the common data generation logic
        logger.debug(f"Generated data: {data}")

        return title, data

    def _data_generator(self) -> Dict[str, Number]:
        """
        Generates a dictionary with human-readable labels for the attributes and their corresponding values.
        """
        logger.debug("Generating data dictionary for State attributes.")
        data = {}

        # Iterate over instance variables (attributes)
        for attr_name, value in vars(self).items():
            # Skip private attributes (those starting with '_')
            if not attr_name.startswith("_"):
                # Generate a human-readable label
                label = self._format_label(attr_name)
                logger.debug(f"Adding attribute: {label} with value: {value}")
                # Add to the data dictionary
                data[label] = value

        logger.debug(f"Final generated data dictionary: {data}")
        return data

    @staticmethod
    def _format_label(field_name: str) -> str:
        """
        Format the attribute name into a human-readable label:
        - Split by underscores
        - Capitalize each word
        - Join with spaces
        """
        logger.debug(f"Formatting label for field name: {field_name}")
        formatted_label = " ".join(word.capitalize() for word in field_name.split("_"))
        logger.debug(f"Formatted label: {formatted_label}")
        return formatted_label

    def get_title(self) -> str:
        """
        Dynamically generate the title from the class name:
        - Split the class name into words
        - Replace "State" with "Stats"
        - Join the words with spaces
        """
        class_name = self.__class__.__name__
        logger.debug(f"Generating title from class name: {class_name}")

        # Split class name at uppercase letters to handle camelCase format
        words = re.sub("([a-z])([A-Z])", r"\1 \2", class_name).split()

        # Replace 'State' with 'Stats' and join the words with spaces
        title = " ".join(words).replace("State", "Stats")
        logger.debug(f"Generated title: {title}")

        return title
