import logging

import aioboto3
from botocore.config import Config

from weather_service.core.events.base import BaseEventStore, Event

LOGGER = logging.getLogger(__name__)


class AwsDynamoDBEventStore(BaseEventStore):
    def __init__(
        self,
        table: str | None = None,
        region: str | None = None,
        endpoint_url: str | None = None,
        aws_access_key_id: str | None = None,
        aws_secret_access_key: str | None = None,
        retries: int = 3,
        read_timeout: int = 10,
        connect_timeout: int = 10,
    ):
        self._table = table
        self._endpoint_url = endpoint_url
        self._region = region
        self._aws_access_key_id = aws_access_key_id
        self._aws_secret_access_key = aws_secret_access_key

        self._config = Config(
            retries={"mode": "standard", "max_attempts": retries},
            read_timeout=read_timeout,
            connect_timeout=connect_timeout,
        )

        self._session: aioboto3.Session | None = None
        self._client_cm = (
            None  # the async context manager returned by session.client(...)
        )
        self._client: aioboto3.Client | None = None

    async def put_event(self, event: Event) -> None:
        assert self._client is not None, "Client not initialized"
        event_dict = {
            "timestamp": event.timestamp.isoformat(),
            "city": event.city,
            "country_code": event.country_code,
            "state": event.state,
            "url": event.url,
        }
        await self._client.put_item(Item=event_dict, TableName=self._table)
        LOGGER.info(f"Pushed event to DynamoDB: {event}")

    async def __aenter__(self) -> "AwsDynamoDBEventStore":
        LOGGER.debug(
            f"Entering AWS DynamoDB event store context manager with table name: {self._table}"
        )
        self._session = aioboto3.Session()
        self._client_cm = self._session.client(
            "dynamodb",
            region_name=self._region,
            endpoint_url=self._endpoint_url,
            aws_access_key_id=self._aws_access_key_id,
            aws_secret_access_key=self._aws_secret_access_key,
            config=self._config,
        )
        # enter the aioboto3 client context
        await self._client_cm.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        LOGGER.debug(
            f"Exiting AWS DynamoDB event store context manager with table name: {self._table}"
        )
        if self._client_cm is not None:
            await self._client_cm.__aexit__(exc_type, exc_val, exc_tb)
        self.client = None
        self._client_cm = None
        self._session = None
