import os
import json
import base64
import logging

import boto3

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize DynamoDB resource and table
_dynamodb = boto3.resource('dynamodb')
_table_name = os.environ['TABLE_NAME']
_table = _dynamodb.Table(_table_name)

def lambda_handler(event, context):
    """
    Kinesis event processor: decodes each record, parses JSON CloudEvent envelope,
    and writes the envelope attributes + data as a DynamoDB item.
    """
    records_processed = 0
    for rec in event.get('Records', []):
        try:
            # Kinesis data is base64-encoded
            payload = base64.b64decode(rec['kinesis']['data']).decode('utf-8')
            item = json.loads(payload)

            # Put the entire CloudEvent as the item
            _table.put_item(Item=item)
            records_processed += 1
        except Exception as e:
            logger.error(f"Error processing record: {e}", exc_info=True)
            # Optionally: send to DLQ by re-raising
            raise

    logger.info(f"Processed {records_processed} records.")
    return {
        'statusCode': 200,
        'body': json.dumps({'processed': records_processed})
    }