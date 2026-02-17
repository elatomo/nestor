"""Weather and location tools."""

import logging
from datetime import UTC, datetime

import httpx
from async_lru import alru_cache
from pydantic import BaseModel
from pydantic_ai import RunContext

from ..dependencies import AssistantDeps

logger = logging.getLogger(__name__)


GEOCODING_API = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_API = "https://api.open-meteo.com/v1/forecast"
# Default timeout in seconds for Open-Meteo API calls
HTTP_TIMEOUT = 30.0

# Weather codes: https://open-meteo.com/en/docs#weather_variable_documentation
WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


class GeoLocation(BaseModel):
    """Resolved geographic location."""

    name: str
    country: str
    latitude: float
    longitude: float
    elevation: float | None = None

    @property
    def osm_url(self) -> str:
        """OpenStreetMap link."""
        return f"https://www.openstreetmap.org/?mlat={self.latitude}&mlon={self.longitude}&zoom=14"


class DailyForecast(BaseModel):
    """Single day forecast summary."""

    date: str
    """ISO date (YYYY-MM-DD)."""

    temp_min: float
    """Minimum temperature in °C."""

    temp_max: float
    """Maximum temperature in °C."""

    precipitation_sum: float
    """Total precipitation in mm (rain + snow)."""

    precipitation_hours: float
    """Hours with precipitation."""

    precipitation_probability_max: int
    """Maximum precipitation probability (0-100%)."""

    wind_speed_max: float
    """Maximum wind speed in km/h."""

    wind_gusts_max: float
    """Maximum wind gusts in km/h."""

    weather_code: int
    """WMO weather code. See weather_description for a description."""

    weather_description: str
    """WMO weather description."""


class WeatherForecast(BaseModel):
    """Multi-day weather forecast."""

    location: str
    elevation: float
    days: list[DailyForecast]


class HourData(BaseModel):
    """Single hour conditions."""

    time: str
    """Hour in HH:MM format (local time)."""

    temp: float
    """Temperature in °C."""

    precipitation_probability: int
    """Probability of precipitation (0-100%)."""

    precipitation: float
    """Precipitation amount in mm."""

    weather_code: int
    """WMO weather code."""

    weather_description: str
    """Human-readable weather condition."""

    is_day: bool
    """True during daylight hours."""


class HourlyForecast(BaseModel):
    """Hourly weather for a single day."""

    location: str
    """Location name."""

    date: str
    """ISO date (YYYY-MM-DD)."""

    hours: list[HourData]
    """24 hours of weather data."""


@alru_cache
async def geocode(query: str) -> GeoLocation | None:
    """Resolve a location name to coordinates.

    Works with:
      - City names: "Madrid", "Barcelona"
      - Geographic features: "Peñalara", "Sierra de Guadarrama"
      - Postal codes: "28001"

    Does NOT work with:
      - Street addresses: "Calle Mayor 1, Madrid"
      - POIs: "Museo del Prado"

    Args:
        query: Location name, city, or postal code

    Returns:
        GeoLocation with coordinates and elevation, or None if not found
    """
    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        r = await client.get(GEOCODING_API, params={"name": query, "count": 1})
        data = r.json()

    if not data.get("results"):
        logger.info("Geocoding failed: no results for %r", query)
        return None

    loc = data["results"][0]
    result = GeoLocation(
        name=loc["name"],
        country=loc["country"],
        latitude=loc["latitude"],
        longitude=loc["longitude"],
        elevation=loc["elevation"],
    )

    logger.info(
        "Geocoded %r → %s, %s (%s)", query, result.name, result.country, result.osm_url
    )

    return result


async def get_weather(
    ctx: RunContext[AssistantDeps],
    location: str | None = None,
    forecast_days: int | None = None,
) -> WeatherForecast | None:
    """Get weather forecast for a location.

    Provides daily summaries including temperature range, precipitation,
    and wind conditions. Useful for planning outdoor activities.

    Args:
        ctx: Agent run context
        location: Location name, city, or postal code. Uses default if not specified.
        forecast_days: Number of days (1-16). Defaults to 3. Use 1 for today,
            5-7 for "this week", etc.

    Returns:
        Weather forecast with daily summaries starting today, or None in case
            of errors or location not found.

    Examples:
        >>> # Weather in the default location for today, tomorrow and the day after
        >>> await get_weather(ctx)

        >>> # Weather in Segovia for today and tomorrow
        >>> await get_weather(ctx, location="Segovia", forecast_days=2)
    """
    location = location or ctx.deps.default_location
    forecast_days = max(1, min(16, forecast_days or 3))
    geo = await geocode(location)
    if not geo:
        return None

    params: dict[str, str | int | float] = {
        "latitude": geo.latitude,
        "longitude": geo.longitude,
        "daily": ",".join(
            [
                "temperature_2m_max",
                "temperature_2m_min",
                "precipitation_sum",
                "precipitation_hours",
                "precipitation_probability_max",
                "wind_speed_10m_max",
                "wind_gusts_10m_max",
                "weather_code",
            ]
        ),
        "timezone": "auto",
        "forecast_days": forecast_days,
    }

    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        r = await client.get(FORECAST_API, params=params)
        data = r.json()

    daily = data["daily"]
    days = [
        DailyForecast(
            date=daily["time"][i],
            temp_min=daily["temperature_2m_min"][i],
            temp_max=daily["temperature_2m_max"][i],
            precipitation_sum=daily["precipitation_sum"][i],
            precipitation_hours=daily["precipitation_hours"][i],
            precipitation_probability_max=daily["precipitation_probability_max"][i],
            wind_speed_max=daily["wind_speed_10m_max"][i],
            wind_gusts_max=daily["wind_gusts_10m_max"][i],
            weather_code=daily["weather_code"][i],
            weather_description=WEATHER_CODES.get(daily["weather_code"][i]),
        )
        for i in range(len(daily["time"]))
    ]

    logger.info("Fetched %d-day forecast for %s", len(days), geo.name)

    return WeatherForecast(
        location=geo.name,
        elevation=geo.elevation,
        days=days,
    )


async def get_hourly_forecast(
    ctx: RunContext[AssistantDeps],
    location: str | None = None,
    date: str | None = None,
) -> HourlyForecast | None:
    """Get hour-by-hour weather for a specific day.

    Useful for planning time-sensitive outdoor activities like hanging laundry,
    running, or hiking. Returns precipitation probability and dry/wet status
    for each hour.

    Args:
        ctx: Agent context
        location: Location name, city, or postal code. Uses default if not specified.
        date: ISO date (YYYY-MM-DD) to get forecast for. Defaults to today.
            Use get_current_date to determine today's date if needed.

    Returns:
        Hourly forecast or None if location not found.
    """
    location = location or ctx.deps.default_location
    target_date = date or datetime.now(UTC).date().isoformat()
    geo = await geocode(location)
    if not geo:
        return None

    params: dict[str, str | float] = {
        "latitude": geo.latitude,
        "longitude": geo.longitude,
        "hourly": ",".join(
            [
                "temperature_2m",
                "precipitation_probability",
                "precipitation",
                "weather_code",
                "is_day",
            ]
        ),
        "timezone": "auto",
        "start_date": target_date,
        "end_date": target_date,
    }

    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        r = await client.get(FORECAST_API, params=params)
        data = r.json()

    hourly = data["hourly"]
    hours = [
        HourData(
            time=hourly["time"][i].split("T")[1][:5],
            temp=hourly["temperature_2m"][i],
            precipitation_probability=hourly["precipitation_probability"][i],
            precipitation=hourly["precipitation"][i],
            weather_code=hourly["weather_code"][i],
            weather_description=WEATHER_CODES.get(hourly["weather_code"][i]),
            is_day=bool(hourly["is_day"][i]),
        )
        for i in range(len(hourly["time"]))
    ]

    logger.info("Fetched hourly forecast for %s on %s", geo.name, target_date)

    return HourlyForecast(
        location=geo.name,
        date=target_date,
        hours=hours,
    )
