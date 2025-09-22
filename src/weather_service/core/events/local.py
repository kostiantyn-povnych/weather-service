import json
import logging
from pathlib import Path

import aiofiles

from weather_service.core.events.base import BaseEventStore, Event

LOGGER = logging.getLogger(__name__)


class LocalEventStore(BaseEventStore):
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.file = None

    async def put_event(self, event: Event) -> None:
        event_dict = {
            "timestamp": event.timestamp.isoformat(),
            "city": event.city,
            "country_code": event.country_code,
            "state": event.state,
            "url": event.url,
        }
        await self.file.write(json.dumps(event_dict) + "\n")
        LOGGER.info(f"Pushed event to local file: {event}")

    async def __aenter__(self) -> "LocalEventStore":
        LOGGER.debug(
            f"Entering local event store context manager with file path: {self.file_path}"
        )
        self.file = await aiofiles.open(self.file_path, "a")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        LOGGER.debug(
            f"Exiting local event store context manager with file path: {self.file_path}"
        )
