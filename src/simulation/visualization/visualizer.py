from src.simulation.grid.grid import Grid
from src.simulation.grid.structure.structure_factory import logger
from src.simulation.people.people import People
from src.simulation.visualization.plotter.grid_plotter import GridPlotter
from src.simulation.visualization.plotter.state_plotter import StatePlotter


class Visualizer:
    def __init__(self) -> None:
        logger.debug("Initializing Visualizer.")
        self._grid_plotter: GridPlotter = GridPlotter()
        logger.debug("GridPlotter initialized.")
        self._state_plotter: StatePlotter = StatePlotter()
        logger.debug("StatePlotter initialized.")

    def display_town_slide_show(self) -> None:
        logger.debug("Displaying town slide show using GridPlotter.")
        self._grid_plotter.show_slide_show()

    def display_simulation_stats(self):
        logger.debug("Displaying simulation statistics using StatePlotter.")
        self._state_plotter.plot()

    def add(self, year: int, grid: Grid, people: People):
        logger.debug(f"Adding data for year {year} to GridPlotter and StatePlotter.")
        logger.debug("Adding grid data to GridPlotter.")
        self._grid_plotter.add(year, grid.get_grid())
        logger.debug("Adding grid and people data to StatePlotter.")
        self._state_plotter.add(year, grid, people)
