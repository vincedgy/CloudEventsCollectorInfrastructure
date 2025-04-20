from aws_cdk import aws_glue as glue
from aws_cdk import aws_iam as iam
from constructs import Construct

class GlueConstruct(Construct):
    def __init__(self, scope: Construct, id: str, bucket):
        super().__init__(scope, id)
        self.role = iam.Role(self, "GlueCrawlerRole",
            assumed_by=iam.ServicePrincipal("glue.amazonaws.com")
        )
        self.role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSGlueServiceRole")
        )
        glue.CfnCrawler(self, "EventsCrawler",
            role=self.role.role_arn,
            database_name=f"{scope.stack_name}_db",
            targets=glue.CfnCrawler.TargetsProperty(
                s3_targets=[glue.CfnCrawler.S3TargetProperty(path=bucket.bucket_arn)]
            )
        )
