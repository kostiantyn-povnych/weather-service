import logging
import os

import aiofiles

from weather_service.core.data_store.base import BaseDataStore

LOGGER = logging.getLogger(__name__)


class LocalFileDataStore(BaseDataStore):
    def __init__(self, directory: str):

        LOGGER.info(f"Initializing local file data store with directory: {directory}")

        if not os.path.exists(directory):
            os.makedirs(directory)

        self.directory = directory

    async def put_object(self, object_name: str, data: bytes) -> str:
        file_path = os.path.join(self.directory, object_name)
        # canonicalize the file path
        file_path = os.path.abspath(file_path)
        LOGGER.info(f"Saving file: {file_path}")

        async with aiofiles.open(file_path, "wb") as f:
            await f.write(data)

        return file_path
