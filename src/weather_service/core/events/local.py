import json
import logging
import os
from pathlib import Path

import aiofiles

from weather_service.core.events.base import BaseEventStore, Event

LOGGER = logging.getLogger(__name__)


class LocalEventStore(BaseEventStore):
    """Local event store that writes events to a file.
    NOT FOR PRODUCTION USE"""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        LOGGER.info(f"Initializing local event store with file path: {file_path}")
        if not os.path.exists(file_path):
            os.makedirs(file_path)

    async def put_event(self, event: Event) -> None:
        async with aiofiles.open(self.file_path, "a") as f:
            event_dict = {
                "timestamp": event.timestamp.isoformat(),
                "city": event.city,
                "country_code": event.country_code,
                "state": event.state,
                "url": event.url,
            }
            await f.write(json.dumps(event_dict) + "\n")

        LOGGER.info(f"Pushed event to local file: {event}")
