from abc import ABC, abstractmethod


class BaseDataStore(ABC):
    @abstractmethod
    async def put_object(self, object_name: str, data: bytes) -> str:
        pass

    @abstractmethod
    async def __aenter__(self) -> "BaseDataStore":
        return self

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        pass
