from aws_cdk import Stack, Environment
from constructs import Construct
from infrastructure.pipeline_construct import PipelineConstruct

class PipelineStack(Stack):
    def __init__(self, scope: Construct, id: str, *, env: Environment):
        super().__init__(scope, id, env=env)

        PipelineConstruct(self, "CICDPipeline", env=env)