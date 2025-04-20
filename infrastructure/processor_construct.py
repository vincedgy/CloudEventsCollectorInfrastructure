from aws_cdk import (
    Duration,
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_sqs as sqs
)
from aws_cdk.aws_lambda_event_sources import KinesisEventSource
from constructs import Construct

class ProcessorConstruct(Construct):
    def __init__(self, scope: Construct, id: str, stream, table):
        super().__init__(scope, id)
        self.dlq = sqs.Queue(self, "StreamDLQ",
            retention_period=Duration.days(14)
        )
        self.role = iam.Role(self, "ProcessorRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com")
        )
        self.role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
        )
        table.grant_write_data(self.role)
        self.fn = _lambda.Function(self, "StreamToDynamoLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="handler.lambda_handler",
            code=_lambda.Code.from_asset("lambda/stream_to_dynamo"),
            role=self.role,
            environment={"TABLE_NAME": table.table_name},
            timeout=Duration.minutes(1)
        )
        self.fn.add_event_source(KinesisEventSource(
            stream=stream,
            starting_position=_lambda.StartingPosition.LATEST,
            batch_size=100,
            bisect_batch_on_error=True,
            retry_attempts=2
        ))
        

