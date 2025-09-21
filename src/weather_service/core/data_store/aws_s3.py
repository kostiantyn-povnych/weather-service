import os

import aioboto3

from weather_service.core.data_store.base import BaseDataStore


class AwsS3DataStore(BaseDataStore):
    def __init__(self, bucket_name: str, folder_name: str):
        self.bucket_name = bucket_name
        self.folder_name = folder_name

    async def put_object(self, object_name: str, data: bytes) -> str:
        session = aioboto3.Session()
        async with session.resource("s3") as s3:
            await s3.Object(
                self.bucket_name, os.path.join(self.folder_name, object_name)
            ).put(Body=data)

            # return the URL of the object
            # TODO: make it configurable (at least for Localstack)
            return f"https://{self.bucket_name}.s3.amazonaws.com/{self.folder_name}/{object_name}"
