#utils.py
import requests
from django.conf import settings

import requests
from django.conf import settings

def get_weather_forecast(lat=12.8911, lon=80.0815):
    """
    Fetches weather forecast data using the OpenWeatherMap One Call API
    and provides advice based on rain prediction.
    
    :param lat: Latitude of the location (default: Vandalur, Chennai)
    :param lon: Longitude of the location (default: Vandalur, Chennai)
    :return: Advice string based on the weather forecast
    """

    # Get the API key from Django settings
    api_key = settings.OPENWEATHER_API_KEY
    
    # OpenWeatherMap API endpoint for One Call API
    url = f"http://api.weatherapi.com/v1/forecast.json?key=04c7bcd904174973b92182555240909&q=Chennai&days=11&aqi=no&alerts=no"
    
    try:
        # Make a request to the OpenWeatherMap API
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses

        # Parse the JSON response
        weather_data = response.json()
        return weather_data
        # rain = weather_data['forecast']['forecastday'][0]['day']['totalprecip_mm']

        # # Check if rain is forecasted in the next day's weather
        # if rain > 2.5:
        #     return f"Reduce power usage by 30% to prepare for reduced input tomorrow, rain mm: {rain}"
        # else:
        #     return f"No need to save power, rain mm: {rain}"
    
    
    except requests.exceptions.RequestException as e:
        return f"Error fetching weather data: {str(e)}"


def check_if_panel_defective(panel_data):
    # Simulate defect detection
    if panel_data['input_power'] <= 0:
        return True
    return False

# utils.py

def calculate_mppt(voltage, current, prev_voltage, prev_current):
    """
    Calculates the Maximum Power Point (MPPT) using the Perturb and Observe method.
    
    :param voltage: The current voltage of the solar panel.
    :param current: The current output of the solar panel.
    :param prev_voltage: The previous voltage of the solar panel.
    :param prev_current: The previous current output of the solar panel.
    :return: The updated voltage and power at the Maximum Power Point.
    """
    
    # Calculate the power at the current and previous points
    power = voltage * current
    prev_power = prev_voltage * prev_current
    
    # Check how the power has changed
    if power > prev_power:
        # If power has increased, continue in the same direction
        next_voltage = voltage + 0.1  # Increment voltage slightly
    else:
        # If power has decreased, reverse the direction
        next_voltage = voltage - 0.1  # Decrement voltage slightly

    # Update current for the new voltage
    # In a real scenario, you would retrieve the actual current for this voltage
    next_current = current  # Placeholder for actual current
    
    return next_voltage, power
