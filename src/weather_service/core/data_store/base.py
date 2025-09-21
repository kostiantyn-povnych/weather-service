from abc import ABC, abstractmethod


class BaseDataStore(ABC):
    @abstractmethod
    async def put_object(self, object_name: str, data: bytes) -> str:
        pass
