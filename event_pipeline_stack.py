from aws_cdk import Stack, Environment
from constructs import Construct
from infrastructure.kinesis_construct import KinesisConstruct
from infrastructure.firehose_construct import FirehoseConstruct
from infrastructure.dynamodb_construct import DynamoDbConstruct
from infrastructure.processor_construct import ProcessorConstruct
from infrastructure.layer_construct import LayerConstruct

class EventPipelineStack(Stack):
    def __init__(self, scope: Construct, id: str, *, env: Environment):
        super().__init__(scope, id, env=env)
        # Provision a Lambda Layer with event_client
        layer = LayerConstruct(self, "EventClientLayer")

        # Core pipeline
        kinesis = KinesisConstruct(self, "Kinesis")
        firehose = FirehoseConstruct(self, "Firehose", stream=kinesis.stream)
        dynamodb = DynamoDbConstruct(self, "DynamoDb")
        ProcessorConstruct(self, "Processor", stream=kinesis.stream, table=dynamodb.table)