import numpy as np
from src.settings import settings
from src.logger import logger

def get_temperature_for_day(day_of_year: int, mean_temp_f: int = 70, amplitude_f: int = 18, std_dev_f: int = 5) -> float:
    """
    Returns the temperature for a given day of the year using a sine wave to model seasonal variations
    and a normal distribution for daily fluctuations (output in Fahrenheit).

    Parameters:
    - day_of_year (int): Day of the year (1-365)
    - mean_temp_f (float): Mean temperature for the year in Fahrenheit
    - amplitude_f (float): Amplitude of the seasonal temperature variation in Fahrenheit
    - std_dev_f (float): Standard deviation for daily fluctuations in Fahrenheit

    Returns:
    - float: Temperature for the given day in Fahrenheit
    """

    # Ensure the day_of_year is within the valid range (1 to 365)
    if not (1 <= day_of_year <= settings.get("days_in_year", 365)):
        logger.error(f"Invalid day_of_year: {day_of_year}. Must be between 1 and 365.")
        raise ValueError("day_of_year must be between 1 and 365")
    logger.debug(f"Getting temperature for day {day_of_year} with mean={mean_temp_f}, amplitude={amplitude_f}, std_dev={std_dev_f}")

    # Calculate the seasonal variation using a sine wave
    seasonal_variation_f = amplitude_f * np.sin(2 * np.pi * (day_of_year - 81) / settings.get("days_in_year", 365))
    logger.debug(f"Seasonal variation for day {day_of_year}: {seasonal_variation_f:.2f}°F")

    # The mean of the normal distribution is the mean_temp adjusted by the seasonal variation
    temp_mean_f = mean_temp_f + seasonal_variation_f
    logger.debug(f"Adjusted mean temperature for day {day_of_year}: {temp_mean_f:.2f}°F")

    # Generate a random temperature based on the normal distribution
    temperature_f = np.random.normal(loc=temp_mean_f, scale=std_dev_f)
    logger.debug(f"Generated temperature for day {day_of_year}: {temperature_f:.2f}°F")

    return temperature_f


if __name__ == "__main__":
    # Example usage:
    for day in range(1, 366):
        temperature = get_temperature_for_day(day)
        print(f"Temperature on day {day}: {temperature:.2f}°F")
