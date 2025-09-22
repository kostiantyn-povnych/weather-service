"""OpenWeather API response models."""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from dataclasses_json import DataClassJsonMixin


@dataclass
class OpenWeatherMainData(DataClassJsonMixin):
    """Main weather data from OpenWeather API."""

    temp: float
    humidity: int
    pressure: float
    feels_like: Optional[float] = None
    temp_min: Optional[float] = None
    temp_max: Optional[float] = None


@dataclass
class OpenWeatherWeatherData(DataClassJsonMixin):
    """Weather description data from OpenWeather API."""

    description: str
    main: Optional[str] = None
    icon: Optional[str] = None


@dataclass
class OpenWeatherWindData(DataClassJsonMixin):
    """Wind data from OpenWeather API."""

    speed: float
    deg: Optional[int] = None
    gust: Optional[float] = None


@dataclass
class OpenWeatherCurrentWeatherResponse(DataClassJsonMixin):
    """Complete current weather response from OpenWeather API."""

    main: OpenWeatherMainData
    weather: List[OpenWeatherWeatherData]
    wind: OpenWeatherWindData
    visibility: Optional[int] = None
    dt: Optional[int] = None
    dt_txt: Optional[str] = None


@dataclass
class OpenWeatherForecastItem(DataClassJsonMixin):
    """Single forecast item from OpenWeather API."""

    main: OpenWeatherMainData
    weather: List[OpenWeatherWeatherData]
    wind: OpenWeatherWindData
    dt_txt: str
    visibility: Optional[int] = None
    dt: Optional[int] = None


@dataclass
class OpenWeatherForecastResponse(DataClassJsonMixin):
    """Forecast response from OpenWeather API."""

    list: List[OpenWeatherForecastItem]
    city: Optional[Dict[str, Any]] = None


@dataclass
class OpenWeatherGeoLocation(DataClassJsonMixin):
    """Geocoding location response from OpenWeather API."""

    name: str
    country: str
    lat: float
    lon: float
    state: Optional[str] = None
    local_names: Optional[Dict[str, str]] = None
