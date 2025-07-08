"""
Weather information tool for getting current weather conditions.
Auto-discovered by the tool loader system.
"""

from agents import function_tool
import logging
import json
from datetime import datetime
import random

logger = logging.getLogger(__name__)

@function_tool()
def get_weather(location: str) -> str:
    """
    Get current weather information for a specified location.
    
    This tool provides weather information including temperature, 
    conditions, humidity, and wind speed for any city or location.
    
    Args:
        location: The city, country, or location to get weather for (e.g., "London, UK", "New York", "Paris")
    
    Returns:
        Current weather information as a formatted string
    
    Examples:
        get_weather("London") -> "London: 15°C, Partly Cloudy, Humidity: 65%, Wind: 12 km/h"
        get_weather("Tokyo, Japan") -> "Tokyo: 22°C, Sunny, Humidity: 45%, Wind: 8 km/h"
    """
    try:
        # Simula dati meteo (in una implementazione reale useresti un'API meteo)
        weather_conditions = [
            "Sunny", "Partly Cloudy", "Cloudy", "Light Rain", 
            "Heavy Rain", "Snow", "Foggy", "Windy", "Stormy"
        ]
        
        # Genera dati casuali realistici
        temperature = random.randint(-10, 35)  # Temperature range
        condition = random.choice(weather_conditions)
        humidity = random.randint(30, 90)
        wind_speed = random.randint(5, 25)
        
        # Formatta la risposta
        weather_info = {
            "location": location.title(),
            "temperature": f"{temperature}°C",
            "condition": condition,
            "humidity": f"{humidity}%",
            "wind_speed": f"{wind_speed} km/h",
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        
        # Formatta output leggibile
        result = (
            f"🌤️ Weather for {weather_info['location']}:\n"
            f"Temperature: {weather_info['temperature']}\n"
            f"Conditions: {weather_info['condition']}\n"
            f"Humidity: {weather_info['humidity']}\n"
            f"Wind Speed: {weather_info['wind_speed']}\n"
            f"Last Updated: {weather_info['last_updated']}\n"
            f"\nNote: This is simulated weather data for demonstration purposes."
        )
        
        logger.info(f"Weather request for {location}")
        return result
        
    except Exception as e:
        logger.error(f"Weather tool error: {e}")
        return f"Error: Could not retrieve weather information for {location}. Please check the location name and try again."
