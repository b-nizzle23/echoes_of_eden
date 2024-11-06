import random
import time
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm
from typing import List
from matplotlib import colors

class GridPlotter:
    def __init__(self):
        self.plots: List[plt.Figure] = []
        self.color_map: dict[str, str] = {}
        # Use a perceptually uniform palette to ensure distinct colors
        self.palette = sns.color_palette("husl", n_colors=100)  # 100 distinct colors
        self.salt = 12345  # Fixed salt for consistency

    def _get_color_for_char(self, char: str) -> str:
        if char not in self.color_map:
            # Hash the character with a fixed salt for consistent results
            hash_value = hash(char + str(self.salt))  # Add salt to the hash
            color_index = abs(hash_value) % len(self.palette)
            color_tuple = self.palette[color_index]
            # Convert the RGB tuple to a hex color string
            hex_color = colors.to_hex(color_tuple)
            self.color_map[char] = hex_color
        return self.color_map[char]

    def add_grid(self, grid: List[List[str]]) -> None:
        fig, ax = plt.subplots(figsize=(8, 8))  # Adjust size as needed
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

        # Plot each grid element with square markers
        square_size = 1  # You can change this if needed
        for row_idx, row in tqdm(
                enumerate(grid), desc="Adding Grid to Plot", total=num_rows
        ):
            for col_idx, char in enumerate(row):
                color = self._get_color_for_char(char)
                ax.scatter(
                    col_idx, row_idx, color=color, s=square_size**2 * 100, marker="s"
                )

        # Add the color legend (key)
        self._add_color_key(ax)

        self.plots.append(fig)

    def _add_color_key(self, ax) -> None:
        """Add a color key showing the terrain types and their associated colors."""
        # Dynamically generate terrain types (for example, we use characters 'a', 'b', 'c', etc.)
        terrain_types = list(self.color_map.keys())  # Use the terrain types from color_map

        # Create a list of scatter objects (one per terrain type)
        handles = []
        for char in terrain_types:
            color = self._get_color_for_char(char)
            handle = plt.Line2D([0], [0], marker="s", color="w", markerfacecolor=color, markersize=10, label=char)
            handles.append(handle)

        # Add the legend
        ax.legend(handles=handles, loc="upper right", fontsize=8, title="Terrain Types")

    def show_slide_show(self, pause_time: float = 2.0) -> None:
        for _, _ in tqdm(
                enumerate(self.plots), desc="Displaying Slideshow", total=len(self.plots)
        ):
            plt.show()
            time.sleep(pause_time)

if __name__ == "__main__":

    def generate_random_grid(size: int, terrain_chars: List[str]) -> List[List[str]]:
        """Generate a random grid with dynamically provided terrain characters."""
        return [
            [random.choice(terrain_chars) for _ in range(size)] for _ in range(size)
        ]

    plotter = GridPlotter()

    # Set grid size dynamically
    grid_size = 100  # You can change this value
    num_grids = 3

    # Dynamically generate terrain types (characters 'a', 'b', 'c', etc.)
    terrain_chars = [i for i in ['b', 'B', 'f', 'F', 'm', 'M', 'h', 'H', ' ', '*']]

    print(f"Generating {num_grids} test grids of size {grid_size}x{grid_size}...")
    test_grids = [
        generate_random_grid(grid_size, terrain_chars)
        for _ in tqdm(range(num_grids), desc="Generating Grids", ncols=100)
    ]

    print("Adding grids to plotter...")
    for test_grid in tqdm(test_grids, desc="Adding Grids to Plotter", ncols=100):
        plotter.add_grid(test_grid)

    print("Displaying slideshow...")
    plotter.show_slide_show(pause_time=2.0)
