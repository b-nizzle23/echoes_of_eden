import numpy as np

from src.simulation.grid.grid import Grid
from src.simulation.grid.location import Location
from src.simulation.grid.structure.work.work import Work
from src.settings import settings

class Farm(Work):
    def __init__(self, grid: Grid, location: Location) -> None:
        max_worker_count: int = settings.get("farm_max_worker_count", 3)
        max_work_count: int = settings.get("farm_max_work_count", 3)
        yield_variance = np.random.normal(loc=settings.get("farm_yield_var_loc", 0),
                                          scale=settings.get("farm_yield_var_scale", 4)
                                          )
        super().__init__(grid,
                         location,
                         settings.get("farm_size", 5),
                         settings.get("farm_size", 5),
                         settings.get("farm_char", "F"),
                         max_worker_count,
                         max_work_count,
                         self._get_yield,
                         yield_variance)

    def _get_yield(self) -> float:
        """
        Yield logic for the Farm class, with a temperature-dependent yield curve.
        The highest yield occurs at 70°F (50 food), with a minimum yield of 25 food at extreme temperatures (40°F or 90°F).

        Returns:
        - float: The yield (food) for the given day based on temperature.
        """
        temp: float = self._grid.get_temperature_for_day()

        # Parameters for temperature-dependent yield curve
        optimal_temp: float = 70  # Optimal temperature for best yield
        std_dev_temp: float = (
            10  # Standard deviation of the temperature curve (how sharply it drops off)
        )

        # Calculate the temperature-dependent yield factor using a Gaussian function
        yield_factor: float = np.exp(
            -((temp - optimal_temp) ** 2) / (2 * std_dev_temp**2)
        )

        # Scale the yield factor to the desired range (25 to 50 food)
        min_yield: float = settings.get("farm_min_yield", 25)
        max_yield: float = settings.get("farm_max_yield", 50)

        # Linearly scale the yield factor to range between min_yield and max_yield
        adjusted_yield: float = min_yield + (max_yield - min_yield) * yield_factor

        # t     y
        # 40	25.1
        # 50	34.9
        # 60	43.7
        # 70	50.0
        # 80	43.7
        # 90	25.1

        return adjusted_yield
