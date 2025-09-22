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

    def id(self) -> str:
        return (
            f"{self.timestamp.isoformat()}_{self.city}_{self.country_code}_{self.state}"
        )


class BaseEventStore(ABC):
    @abstractmethod
    async def put_event(self, event: Event) -> None:
        pass

    # @abstractmethod
    # async def __aenter__(self) -> "BaseEventStore":
    #     return self

    # @abstractmethod
    # async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
    #     pass
