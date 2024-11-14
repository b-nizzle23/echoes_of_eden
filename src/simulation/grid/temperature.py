import numpy as np


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
    if not (1 <= day_of_year <= 365):
        raise ValueError("day_of_year must be between 1 and 365")

    # Calculate the seasonal variation using a sine wave
    # Sine wave oscillates between -1 and 1, we scale it by the amplitude.
    seasonal_variation_f = amplitude_f * np.sin(2 * np.pi * (day_of_year - 81) / 365)

    # The mean of the normal distribution is the mean_temp adjusted by the seasonal variation
    temp_mean_f = mean_temp_f + seasonal_variation_f

    # Generate a random temperature based on the normal distribution
    temperature_f = np.random.normal(loc=temp_mean_f, scale=std_dev_f)

    return temperature_f


if __name__ == "__main__":
    # Example usage:
    for day in range(1, 366):
        temperature = get_temperature_for_day(day)
        print(f"Temperature on day {day}: {temperature:.2f}°F")
