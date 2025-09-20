import os
import aiofiles

from data_store.base import BaseDataStore


class LocalFileDataStore(BaseDataStore):
    def __init__(self, directory: str):
        self.directory = directory

    async def upload_file(self, object_name: str, data: bytes):
        file_path = os.path.join(self.directory, object_name)
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(data)
