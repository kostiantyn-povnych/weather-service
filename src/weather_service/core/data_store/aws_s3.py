import os

import aioboto3

from weather_service.core.data_store.base import BaseDataStore


class AwsS3DataStore(BaseDataStore):
    def __init__(self, bucket_name: str, folder_name: str):
        self.bucket_name = bucket_name
        self.folder_name = folder_name

    async def upload_file(self, object_name: str, data: bytes):
        session = aioboto3.Session()
        async with session.resource("s3") as s3:
            await s3.Object(
                self.bucket_name, os.path.join(self.folder_name, object_name)
            ).put(Body=data)
