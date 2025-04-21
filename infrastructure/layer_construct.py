from aws_cdk import aws_lambda as _lambda, RemovalPolicy
from constructs import Construct
import os

class LayerConstruct(Construct):
    def __init__(self, scope: Construct, id: str):
        super().__init__(scope, id)
        # Build a Lambda Layer from the local event_client package
        self.layer = _lambda.LayerVersion(
            self,
            "EventClientLayer",
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_9, _lambda.Runtime.PYTHON_3_10],
            code=_lambda.Code.from_asset(
                os.path.join(os.getcwd(), "lambda", "layers")
            ),
            description="Lambda layer containing the event_client library",
            removal_policy=RemovalPolicy.RETAIN
        )