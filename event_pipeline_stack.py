from aws_cdk import Stack, Environment
from constructs import Construct
from infrastructure.kinesis_construct import KinesisConstruct
from infrastructure.firehose_construct import FirehoseConstruct
from infrastructure.dynamodb_construct import DynamoDbConstruct
from infrastructure.processor_construct import ProcessorConstruct
from infrastructure.glue_construct import GlueConstruct

class EventPipelineStack(Stack):
    def __init__(self, scope: Construct, id: str, *, env: Environment):
        super().__init__(scope, id, env=env)

        kinesis = KinesisConstruct(self, "Kinesis")
        firehose = FirehoseConstruct(self, "Firehose", stream=kinesis.stream)
        dynamodb = DynamoDbConstruct(self, "DynamoDb")
        ProcessorConstruct(self, "Processor", stream=kinesis.stream, table=dynamodb.table)
        GlueConstruct(self, "Glue", bucket=firehose.raw_bucket)