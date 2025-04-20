from aws_cdk import (
    pipelines as pipelines_mod,
    aws_codecommit as codecommit,
    Environment
)
from constructs import Construct
from aws_cdk.pipelines import CodePipeline, CodePipelineSource, ShellStep, CodeBuildStep
from event_pipeline_stack import EventPipelineStack
from aws_cdk import Stage

class EventPipelineAppStage(Stage):
    def __init__(self, scope: Construct, id: str, *, env: Environment):
        super().__init__(scope, id, env=env)
        EventPipelineStack(self, "EventPipeline", env=env)

class PipelineConstruct(Construct):
    def __init__(self, scope: Construct, id: str, *, env: Environment):
        super().__init__(scope, id)

        # CodeCommit repository
        repo = codecommit.Repository(self, "Repo",
            repository_name="event-pipeline-repo"
        )

        # CDK Pipeline
        pipeline = CodePipeline(self, "Pipeline",
            pipeline_name="EventPipelineCI",
            synth=ShellStep("Synth",
                input=CodePipelineSource.code_commit(repo, "main"),
                install_commands=[
                    "python3 -m pip install --upgrade pip",
                    "pip install -r requirements.txt",
                    "npm install -g aws-cdk"
                ],
                commands=[
                    "cdk synth"
                ]
            )
        )

        # Deploy stage
        pipeline.add_stage(
            EventPipelineAppStage(self, "Deploy",
                env=env
            )
        )
