from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Location:
    """Location data model."""

    latitude: float
    longitude: float
    name: str
    local_names: dict[str, str]
    country: str
    state: str | None
    """Optional state of the country. Not all countries have states."""


class GeoCodeLocationProvider(ABC):
    """Abstract base class for geo code location providers."""

    @abstractmethod
    async def resolve_locations(
        self, city: str, country_code: str | None = None, state: str | None = None
    ) -> list[Location]:
        """Resolve a location from a city name and country code."""
        pass
