import json
import logging
from pathlib import Path

import aiofiles

from events.base import BaseEventStore, Event

LOGGER = logging.getLogger(__name__)


class LocalEventStore(BaseEventStore):
    def __init__(self, file_path: Path):
        self.file_path = file_path

    async def store_event(self, event: Event) -> None:

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
