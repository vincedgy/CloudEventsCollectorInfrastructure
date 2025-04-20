from aws_cdk import (
    Duration,
    aws_kinesis as kinesis,
    aws_iam as iam
)
from constructs import Construct

class KinesisConstruct(Construct):
    def __init__(self, scope: Construct, id: str):
        super().__init__(scope, id)
        self.stream = kinesis.Stream(self, "EventStream",
            stream_name="event-stream",
            shard_count=1,
            retention_period=Duration.days(1)
        )
        self.producer_role = iam.Role(self, "ProducerRole",
            assumed_by=iam.AccountRootPrincipal()
        )
        self.producer_role.add_to_policy(iam.PolicyStatement(
            actions=["kinesis:PutRecord"],
            resources=[self.stream.stream_arn]
        ))