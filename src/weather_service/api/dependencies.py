"""FastAPI dependencies for the weather service API."""

from fastapi import Query

from weather_service.api.models import CityQueryParams


def get_city_query_params(
    city: str = Query(
        ...,
        description="Name of the city to get weather for",
        example="London",
        min_length=1,
        max_length=100,
    ),
    country_code: str = Query(
        None,
        description="ISO 3166-1 alpha-2 country code to narrow down the search",
        example="GB",
        pattern=r"^[A-Z]{2}$",
        nullable=True,
    ),
    state: str = Query(
        None,
        description="State or province name to narrow down the search",
        example="England",
        nullable=True,
        max_length=100,
    ),
) -> CityQueryParams:
    """Dependency to extract common city query parameters."""
    return CityQueryParams(
        city=city,
        country_code=country_code,
        state=state,
    )
