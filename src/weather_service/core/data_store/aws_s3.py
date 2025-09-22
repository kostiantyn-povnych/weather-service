import logging
import os

import aioboto3

from weather_service.core.data_store.base import BaseDataStore

LOGGER = logging.getLogger(__name__)


class AwsS3DataStore(BaseDataStore):
    def __init__(
        self, aws_session: aioboto3.Session, bucket_name: str, folder_name: str
    ):
        self.bucket_name = bucket_name
        self.folder_name = folder_name
        self._aws_session = aws_session

    async def put_object(self, object_name: str, data: bytes) -> str:
        async with self._aws_session.resource("s3") as s3:
            object = await s3.Object(
                self.bucket_name, os.path.join(self.folder_name, object_name)
            )
            await object.put(Body=data)

            return f"https://{self.bucket_name}.s3.amazonaws.com/{self.folder_name}/{object_name}"
