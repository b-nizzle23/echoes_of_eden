import random
import time
from typing import Dict, List

import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import colors
from tqdm import tqdm

from src.settings import settings
from src.simulation.grid.structure.structure_factory import logger


class GridPlotter:
    def __init__(self):
        # Initialize the years dictionary to store plot figures
        self._years: Dict[int, plt.Figure] = {}
        logger.debug("Initialized _years dictionary to store plot figures.")

        # Initialize color map dictionary for storing color assignments
        self._color_map: dict[str, str] = {}
        logger.debug("Initialized _color_map dictionary for color assignments.")

        # Use a perceptually uniform palette to ensure distinct colors
        self._palette = sns.color_palette("husl", n_colors=100)  # 100 distinct colors
        logger.debug("Initialized color palette with 100 distinct colors using 'husl'.")

        # Set a fixed salt for consistency
        self._salt = 12345
        logger.debug(f"Initialized fixed salt value: {self._salt}")

    def _get_color_for_char(self, char: str) -> str:
        if char not in self._color_map:
            # Hash the character with a fixed salt for consistent results
            hash_value = hash(char + str(self._salt))  # Add salt to the hash
            color_index = abs(hash_value) % len(self._palette)
            color_tuple = self._palette[color_index]

            # Convert the RGB tuple to a hex color string
            hex_color = colors.to_hex(color_tuple)

            # Log the color generation process
            logger.debug(f"Generated new color for '{char}': {hex_color}")

            # Store the color for future use
            self._color_map[char] = hex_color
        else:
            # Log when the color is being retrieved from the map
            logger.debug(f"Retrieved existing color for '{char}': {self._color_map[char]}")

        return self._color_map[char]

    def add(self, year: int, grid: List[List[str]]) -> None:
        logger.info(f"Adding grid snapshot for year {year}...")

        fig, ax = plt.subplots(
            figsize=(settings.get("fig_size", 8), settings.get("fig_size", 8))
        )  # Adjust size as needed
        ax.set_title("Grid Snapshot")
        ax.set_xlabel("X Axis (Column index)")
        ax.set_ylabel("Y Axis (Row index)")

        # Determine the grid size
        num_rows = len(grid)
        num_cols = len(grid[0])

        # Adjust plot limits to fit the squares tightly
        ax.set_xlim(0, num_cols)
        ax.set_ylim(num_rows, 0)  # Reverse Y-axis to match typical grid coordinates
        ax.axis("off")  # Turn off axes and labels

        logger.debug(f"Grid size: {num_rows} rows, {num_cols} columns.")
        logger.info("Starting to plot each grid element...")

        # Plot each grid element with square markers
        square_size = 1  # You can change this if needed
        for row_idx, row in tqdm(enumerate(grid), desc="Adding Grid to Plot", total=num_rows):
            for col_idx, char in enumerate(row):
                color = self._get_color_for_char(char)
                ax.scatter(col_idx, row_idx, color=color, s=square_size ** 2 * 100, marker="s")

        # Add the color legend (key)
        logger.info("Adding color legend to the plot...")
        self._add_color_key(ax)

        # Store the figure for this year
        self._years[year] = fig
        logger.info(f"Grid snapshot for year {year} added successfully.")


    def _add_color_key(self, ax) -> None:
            """Add a color key showing the terrain types and their associated colors."""
            # Dynamically generate terrain types (for example, we use characters 'a', 'b', 'c', etc.)
            terrain_types = list(self._color_map.keys())  # Use the terrain types from color_map

            # Create a list of scatter objects (one per terrain type)
            handles = []
            for char in terrain_types:
                color = self._get_color_for_char(char)
                handle = plt.Line2D(
                    [0],
                    [0],
                    marker="s",
                    color="w",
                    markerfacecolor=color,
                    markersize=10,
                    label=char,
                )
                handles.append(handle)

            # Add the legend
            ax.legend(handles=handles, loc="upper right", fontsize=8, title="Terrain Types")
            logger.info("Color key added to the plot.")

    def show_slide_show(self, pause_time: float = 2.0) -> None:
        """Displays a slideshow of the stored figures."""
        logger.info("Starting slideshow...")

        for year, fig in tqdm(self._years.items(), desc="Displaying Slideshow", total=len(self._years)):
            plt.show()
            logger.info(f"Displayed slide for year {year}.")
            time.sleep(pause_time)

        logger.info("Slideshow completed.")


if __name__ == "__main__":

    def generate_random_grid(size: int, terrain_chars: List[str]) -> List[List[str]]:
        """Generate a random grid with dynamically provided terrain characters."""
        logger.debug(f"Generating a grid of size {size}x{size} with terrain types: {terrain_chars}")
        return [[random.choice(terrain_chars) for _ in range(size)] for _ in range(size)]

    plotter = GridPlotter()

    # Set grid size dynamically
    grid_size = settings.get("grid_size", 100)  # You can change this value
    num_grids = settings.get("num_grids", 3)

    # Dynamically generate terrain types (characters 'a', 'b', 'c', etc.)
    terrain_types = [
        settings.get("home_construction_char", "h"),
        settings.get("home_char", "H"),
        settings.get("barn_construction_char", "b"),
        settings.get("barn_char", "B"),
        settings.get("farm_construction_char", "f"),
        settings.get("farm_char", "F"),
        settings.get("mine_construction_char", "m"),
        settings.get("mine_char", "M"),
        settings.get("empty_char", " "),
        settings.get("tree_char", "*"),
    ]
    terrain_chars = [i for i in terrain_types]

    # Log grid generation details
    logger.info(f"Generating {num_grids} test grids of size {grid_size}x{grid_size}...")
    test_grids = [
        generate_random_grid(grid_size, terrain_chars)
        for _ in tqdm(range(num_grids), desc="Generating Grids", ncols=100)
    ]

    # Log grid addition to plotter
    logger.info("Adding grids to plotter...")
    for test_grid in tqdm(test_grids, desc="Adding Grids to Plotter", ncols=100):
        plotter.add(years, test_grid)  # todo: pass in proper years value

    # Log slideshow display
    logger.info("Displaying slideshow...")
    plotter.show_slide_show(pause_time=2.0)
