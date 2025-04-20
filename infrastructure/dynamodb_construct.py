from aws_cdk import aws_dynamodb as dynamodb
from constructs import Construct

class DynamoDbConstruct(Construct):
    def __init__(self, scope: Construct, id: str):
        super().__init__(scope, id)
        self.table = dynamodb.Table(self, "EventsTable",
            partition_key=dynamodb.Attribute(
                name="application_name", type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="timestamp", type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST
        )
        self.table.add_global_secondary_index(
            index_name="eventIdIndex",
            partition_key=dynamodb.Attribute(
                name="event_id", type=dynamodb.AttributeType.STRING
            ),
            projection_type=dynamodb.ProjectionType.ALL
        )