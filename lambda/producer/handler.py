import os
import json
from event_client import send_event # type: ignore

def lambda_handler(event, context):
    """
    Receives an API Gateway proxy event, constructs and sends a CloudEvent via Kinesis.

    Expects:
      - body: JSON string or object
      - pathParameters.id for optional subject

    Environment variables:
      EVENT_STREAM_NAME
      APPLICATION_NAME
      EVENT_TYPE
    """
    # Parse payload
    body = event.get("body")
    if isinstance(body, str):
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            payload = {"raw": body}
    else:
        payload = body or {}

    # Read configuration
    application_name = os.getenv("APPLICATION_NAME") or "lambda_producer"
    subject = event.get("pathParameters", {}).get("id")
    extensions = {"source": "lambda_producer"}

    # Send event
    event_id = send_event(
        application_name=application_name,
        payload=payload,
        subject=subject,
        extensions=extensions,
        metadata={}
    )

    # Return success
    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Event dispatched", "event_id": event_id})
    }

