from aws_cdk import (
    Duration,
    aws_lambda as _lambda,
    aws_iam as iam
)
from constructs import Construct

class EventProducer(Construct):
    def __init__(self, scope: Construct, id: str):
        super().__init__(scope, id)
        self.role = iam.Role(self, "ProcessorRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com")
        )
        self.role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
        )
        self.fn = _lambda.Function(self, "StreamToDynamoLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="handler.lambda_handler",
            code=_lambda.Code.from_asset("lambda/client/event_producer"),
            role=self.role,
            timeout=Duration.minutes(1)
        )        

