from numbers import Number
from typing import Dict

import seaborn as sns
from matplotlib import pyplot as plt

from src.simulation.grid.grid import Grid
from src.simulation.grid.structure.structure_factory import logger
from src.simulation.people.people import People
from src.simulation.visualization.state.grid_disaster_state import \
    GridDisasterState
from src.simulation.visualization.state.grid_state import GridState
from src.simulation.visualization.state.people_disaster_state import \
    PeopleDisasterState
from src.simulation.visualization.state.people_state import PeopleState
from src.simulation.visualization.state.resource_state import ResourceState
from src.simulation.visualization.state.task_state import TaskState


class StatePlotter:
    def __init__(self):
        # { title: { year: { label: number } } }
        self._states: Dict[str, Dict[int, Dict[str, Number]]] = {}

    def add(self, year: int, grid: Grid, people: People):
        # Define state classes to process
        states = [
            GridDisasterState(grid),
            GridState(grid),
            PeopleDisasterState(people),
            PeopleState(people),
            ResourceState(grid),
            TaskState(people),
        ]

        # Add data for each state class
        for state in states:
            title, data = state.get_data()

            # Log state data being added
            logger.debug(f"Adding data for state: {title}, Year: {year}")
            for label, value in data.items():
                logger.debug(f"  Label: {label}, Value: {value}")

            # Add data to the _states dictionary
            self._add_state_data(title, year, data)

    def _add_state_data(self, title: str, year: int, data: Dict[str, Number]):
        """
        Helper method to add data to the states dictionary.
        Ensures that the state is initialized if it doesn't exist.
        """
        if title not in self._states:
            self._states[title] = {}
            # Log when a new state title is initialized
            logger.debug(f"Initializing new state category: {title}")

        self._states[title][year] = data
        # Log when state data is added for a specific year
        logger.debug(f"Added data for state: {title}, Year: {year}")
        for label, value in data.items():
            logger.debug(f"  Label: {label}, Value: {value}")

    def plot(self):
        """
        Generate plots for each state category stored in `_states`.
        Each title in `_states` will get its own plot with data for each year.
        """
        logger.debug("Generating plots for each state category.")
        for title, data in self._states.items():
            # Log the plotting of each title
            logger.debug(f"Plotting data for state: {title} with {len(data)} years of data.")
            self._plot(title, data)

    @staticmethod
    def _plot(title: str, lines: Dict[int, Dict[str, Number]]):
        """
        Plots lines for each label over the years.

        :param title: A string to be used as the title of the plot. Default is "Line Plot of Data Over Years".
        :param lines: A dictionary where keys are years (int) and values are dictionaries,
                      where each dictionary maps labels (str) to numerical values (int/float).
        """
        # Log the start of the plotting process
        logger.debug(f"Preparing to plot: {title}")

        # Prepare data for plotting
        years = sorted(lines.keys())

        # Log the years being considered
        logger.debug(f"Years to plot: {years}")

        # We will store data for each label over time
        labels_data = {}

        # Loop through each year and accumulate the data for each label
        for year in years:
            year_data = lines[year]  # The data for this year is a dictionary of {label: value}

            for label, value in year_data.items():
                if label not in labels_data:
                    labels_data[label] = {"years": [], "values": []}
                labels_data[label]["years"].append(year)
                labels_data[label]["values"].append(value)

            # Log the data processed for the current year
            logger.debug(f"Year {year}: Processed {len(year_data)} labels")

        # Log the number of labels being plotted
        logger.debug(f"Labels to plot: {list(labels_data.keys())}")

        # Now plot the lines for each label
        plt.figure(figsize=(10, 6))

        for label, data in labels_data.items():
            # Log the plotting of each label
            logger.debug(f"Plotting label: {label}")
            sns.lineplot(x=data["years"], y=data["values"], label=label)

        # Add titles and labels
        plt.title(title)
        plt.xlabel("Year")
        plt.ylabel("Value")
        plt.legend(title="Labels")

        # Show the plot
        logger.debug(f"Displaying the plot: {title}")
        plt.show()
