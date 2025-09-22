import logging
import os

import aioboto3

from weather_service.core.data_store.base import BaseDataStore

LOGGER = logging.getLogger(__name__)


class AwsS3DataStore(BaseDataStore):
    def __init__(self, bucket_name: str, folder_name: str):
        self.bucket_name = bucket_name
        self.folder_name = folder_name
        self.session = None

    async def put_object(self, object_name: str, data: bytes) -> str:
        async with self.session.resource("s3") as s3:
            object = await s3.Object(
                self.bucket_name, os.path.join(self.folder_name, object_name)
            )
            await object.put(Body=data)

            # return the URL of the object
            # TODO: make it configurable (at least for Localstack)
            return f"https://{self.bucket_name}.s3.amazonaws.com/{self.folder_name}/{object_name}"

    async def __aenter__(self) -> "AwsS3DataStore":
        LOGGER.debug(
            f"Entering AWS S3 data store context manager with bucket name: {self.bucket_name}"
        )
        self.session = aioboto3.Session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        LOGGER.debug(
            f"Exiting AWS S3 data store context manager with bucket name: {self.bucket_name}"
        )
        await self.session.close()
