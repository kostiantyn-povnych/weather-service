import logging

import aioboto3

from events.base import BaseEventStore, Event

LOGGER = logging.getLogger(__name__)


class AwsDynamoDBEventStore(BaseEventStore):
    def __init__(self, table_name: str):
        self.table_name = table_name

    async def store_event(self, event: Event) -> None:
        session = aioboto3.Session()
        async with session.resource("dynamodb") as dynamodb:
            table = dynamodb.Table(self.table_name)
            await table.put_item(Item=event.model_dump())
            LOGGER.info(f"Pushed event to DynamoDB: {event}")
