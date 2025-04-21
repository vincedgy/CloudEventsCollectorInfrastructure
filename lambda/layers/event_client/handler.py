import os
import json
import uuid
from datetime import datetime, timezone

import boto3
from botocore.exceptions import ClientError

_stream_name = os.getenv("EVENT_STREAM_NAME", "default-stream")
_kinesis = boto3.client("kinesis")

def send_event(application_name: str, payload: dict, metadata: dict = None) -> str:
    """
    Send a structured event to Kinesis Data Stream.

    :param application_name: logical name of the app
    :param payload: dict of event data
    :param metadata: optional dict of extra metadata
    :return: event_id
    :raises: ClientError on AWS failures
    """
    event_id = str(uuid.uuid4())
    event = {
        "event_id": event_id,
        "application_name": application_name,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "payload": payload,
    }
    if metadata:
        event["metadata"] = metadata

    data_bytes = json.dumps(event).encode("utf-8")
    try:
        _kinesis.put_record(
            StreamName=_stream_name,
            PartitionKey=application_name,
            Data=data_bytes
        )
    except ClientError:
        # optional: add retries/backoff here
        raise
    return event_id
