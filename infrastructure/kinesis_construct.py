from aws_cdk import (
    Stack,
    Duration,
    aws_kinesis as kinesis,
    aws_iam as iam
)
from constructs import Construct

class KinesisConstruct(Construct):
    def __init__(self, scope: Construct, id: str):
        super().__init__(scope, id)
        self.stream = kinesis.Stream(self, "EventStreamProducer",
            stream_name=f"event-stream-{Stack.of(self).stack_name}",  # Add stack name for uniqueness
            encryption=kinesis.StreamEncryption.MANAGED,
            retention_period=Duration.hours(24),
            stream_mode=kinesis.StreamMode.ON_DEMAND
        )
        self.producer_role = iam.Role(self, "ProducerRole",
            assumed_by=iam.AccountRootPrincipal()
        )
        self.producer_role.add_to_policy(iam.PolicyStatement(
            actions=["kinesis:PutRecord"],
            resources=[self.stream.stream_arn]
        ))