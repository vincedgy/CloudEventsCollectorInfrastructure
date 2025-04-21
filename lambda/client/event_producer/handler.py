import json
from event_client.client import send_event # type: ignore
import logging

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """
    Producer of an event
    """
    try:
        # Send an event
        payload = {"order_id": 1234, "status": "created"}
        ce_id = send_event(
          application_name="orders_api",
          event_type="com.mycompany.orders.created",
          data=payload,
          subject="order/1234",
          extensions={"env": "test"}
        )
    except Exception as e:
        logger.error(f"Error processing record: {e}", exc_info=True)
        raise

    logger.info(f"Sent {ce_id} event.")
    return {
        'statusCode': 200,
        'body': json.dumps({'processed': ce_id})
    }