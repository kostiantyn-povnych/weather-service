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
            await f.write(event.model_dump_json() + "\n")
            LOGGER.info(f"Pushed event to local file: {event}")
