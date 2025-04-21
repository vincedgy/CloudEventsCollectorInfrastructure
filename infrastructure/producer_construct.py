from aws_cdk import (
    Duration,
    aws_lambda as _lambda,
    aws_iam as iam
)
from aws_cdk.aws_lambda_event_sources import ApiEventSource
from constructs import Construct

class ProducerConstruct(Construct):
    def __init__(self, scope: Construct, id: str, *, layer: _lambda.ILayerVersion, stream):
        super().__init__(scope, id)
        # IAM role for producer Lambda
        role = iam.Role(self, "ProducerRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com")
        )
        stream.grant_put_records(role)
        role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
        )

        # Producer Lambda function
        fn = _lambda.Function(self, "ProducerLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="handler.lambda_handler",
            code=_lambda.Code.from_asset("lambda/producer"),
            role=role,
            layers=[layer],
            environment={
                "EVENT_STREAM_NAME": stream.stream_name,
                "APPLICATION_NAME": "producer_lambda",
                "EVENT_TYPE": "com.mycompany.producer.event"
            },
            timeout=Duration.seconds(30)
        )

        # (Optional) Add an API Gateway trigger
        fn.add_event_source(ApiEventSource(
            path="/event",
            method="POST"
        ))

