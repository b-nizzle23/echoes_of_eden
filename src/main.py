import os
import argparse
from dotenv import load_dotenv
from src.logger import setup_logger, logger
from src.simulation.simulation import Simulation
from typing import Optional

from src.simulation.result.stats import Stats


def main() -> None:
    environment: str = get_environment()
    setup_logger(mode=environment)

    logger.info("Starting the simulation program.")

    load_dotenv(f"../env/{environment}.env")
    logger.debug(f"Loaded environment variables from ../env/{environment}.env")

    max_simulations: int = int(os.getenv("MAX_SIMULATIONS", "10"))
    actions_per_day: int = int(os.getenv("ACTIONS_PER_DAY", "5"))
    days_per_year: int = int(os.getenv("DAYS_PER_YEAR", "365"))
    years: int = int(os.getenv("YEARS", "50"))
    grid_size: int = int(os.getenv("GRID_SIZE", "100"))

    logger.info(
        f"Configuration: ACTIONS_PER_DAY={actions_per_day}, DAYS_PER_YEAR={days_per_year}, YEARS={years}, GRID_SIZE={grid_size}"
    )

    for i in range(max_simulations):
        logger.info(f"Running simulation {i + 1}")
        simulation: Simulation = Simulation(
            actions_per_day, days_per_year, years, grid_size
        )
        stats: Optional[Stats] = simulation.run()
        logger.info(f"Simulation {i + 1} completed with stats: {stats}")

        # TODO display stats


def get_environment() -> str:
    parser = argparse.ArgumentParser(description="Run the simulation program.")
    parser.add_argument(
        "--env", type=str, default="dev", help="Specify the environment (default: dev)"
    )
    args = parser.parse_args()
    return args.environment


if __name__ == "__main__":
    main()
