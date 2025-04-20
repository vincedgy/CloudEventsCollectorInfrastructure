import os
import aws_cdk as cdk
from pipeline_stack import PipelineStack

app = cdk.App()
environment = cdk.Environment(
    account=os.getenv('CDK_DEFAULT_ACCOUNT'),
    region=os.getenv('CDK_DEFAULT_REGION')
)

# Only deploy the pipeline; it will synth & deploy the EventPipelineStack
PipelineStack(app, "CICDPipelineStack", env=environment)
app.synth()