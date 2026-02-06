"""Weather and location tools."""

import logging

import httpx
from async_lru import alru_cache
from pydantic import BaseModel

logger = logging.getLogger(__name__)

GEOCODING_API = "https://geocoding-api.open-meteo.com/v1/search"


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
    async with httpx.AsyncClient() as client:
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
