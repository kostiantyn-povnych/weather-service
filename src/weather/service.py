from weather.providers.base import Location, WeatherProvider


class WeatherService:
    def __init__(self, provider: WeatherProvider):
        self.provider = provider

    async def get_weather(self, location):
        return await self.provider.get_current_weather(location)

    async def get_weather_forecast(self, location: Location, days: int = 5):
        return await self.provider.get_weather_forecast(location, days)

    async def search_location(self, query: str):
        return await self.provider.search_location(query)

    async def get_weather_by_city(
        self, city_name: str, country_code: str | None = None
    ):
        """Get weather data by city name using the provider."""
        return await self.provider.get_weather_by_city(city_name, country_code)
