from abc import ABC, abstractmethod


class BaseDataStore(ABC):
    @abstractmethod
    async def upload_file(self, object_name: str, data: bytes):
        pass
