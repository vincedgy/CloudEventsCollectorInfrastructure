from aws_cdk import (
    pipelines as pipelines_mod,
    Environment,
    SecretValue,
    aws_secretsmanager as secretsmanager
)
from aws_cdk.pipelines import CodePipeline, CodePipelineSource, ShellStep
from aws_cdk import Stage
from constructs import Construct
from event_pipeline_stack import EventPipelineStack

class EventPipelineAppStage(Stage):
    def __init__(self, scope: Construct, id: str, *, env: Environment):
        super().__init__(scope, id, env=env)
        EventPipelineStack(self, "EventPipeline", env=env)

class PipelineConstruct(Construct):
    def __init__(self, scope: Construct, id: str, *, env: Environment):
        super().__init__(scope, id)

        # Create or import GitHub token secret
        github_secret = secretsmanager.Secret(self, "GitHubTokenSecret",
            secret_name="github-token-secret",
            description="GitHub OAuth token for CodePipeline GitHub source",
            generate_secret_string=secretsmanager.SecretStringGenerator(
                secret_string_template="{}",
                generate_string_key="token",
                exclude_punctuation=True,
                include_space=False
            )
        )

        # Source from GitHub using the secret
        source = CodePipelineSource.git_hub(
            repo_string="vincedgy/CloudEventsCollectorInfrastructure",  # replace with your GitHub repo
            branch="main",
            authentication=SecretValue.secrets_manager(github_secret.secret_name)
        )

        # CDK Pipeline
        pipeline = CodePipeline(self, "Pipeline",
            pipeline_name="EventPipelineCI",
            synth=ShellStep("Synth",
                input=source,
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

        # Deploy stage containing the EventPipelineStack
        pipeline.add_stage(
            EventPipelineAppStage(self, "Deploy", env=env)
        )