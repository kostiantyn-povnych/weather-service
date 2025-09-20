from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime as dt


@dataclass
class Event:
    timestamp: dt
    city: str
    country_code: str
    state: str | None
    url: str


class BaseEventStore(ABC):
    @abstractmethod
    async def store_event(self, event: Event) -> None:
        pass
