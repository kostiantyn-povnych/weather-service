import logging

import aioboto3

from weather_service.core.events.base import BaseEventStore, Event

LOGGER = logging.getLogger(__name__)


class AwsDynamoDBEventStore(BaseEventStore):
    def __init__(
        self,
        aws_session: aioboto3.Session,
        table: str | None = None,
    ):
        self._table = table
        self._aws_session = aws_session

    async def put_event(self, event: Event) -> None:

        async with self._aws_session.client("dynamodb") as dynamo_db_client:
            event_dict = {
                "id": {"S": event.id()},
                "timestamp": {"S": event.timestamp.isoformat()},
                "city": {"S": event.city},
                "country_code": {"S": event.country_code},
                "state": {"S": event.state} if event.state else {"NULL": ""},
                "url": {"S": event.url},
            }
            await dynamo_db_client.put_item(Item=event_dict, TableName=self._table)

        LOGGER.info(f"Pushed event to DynamoDB: {event}")
