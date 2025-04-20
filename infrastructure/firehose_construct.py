from aws_cdk import (
    Duration,
    RemovalPolicy,
    aws_s3 as s3,
    aws_iam as iam,
    aws_kinesisfirehose as firehose
)
from constructs import Construct

class FirehoseConstruct(Construct):
    def __init__(self, scope: Construct, id: str, stream):
        super().__init__(scope, id)
        self.raw_bucket = s3.Bucket(self, "RawEventsBucket",
            bucket_name=f"{scope.stack_name.lower()}-raw-events",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            lifecycle_rules=[
                s3.LifecycleRule(
                    transitions=[
                        s3.Transition(
                            storage_class=s3.StorageClass.INFREQUENT_ACCESS,
                            transition_after=Duration.days(30)
                        )
                    ],
                    expiration=Duration.days(365)
                )
            ]
        )
        self.firehose_role = iam.Role(self, "FirehoseRole",
            assumed_by=iam.ServicePrincipal("firehose.amazonaws.com")
        )
        self.raw_bucket.grant_read_write(self.firehose_role)
        firehose.CfnDeliveryStream(self, "FirehoseToS3",
            kinesis_stream_source_configuration=
                firehose.CfnDeliveryStream.KinesisStreamSourceConfigurationProperty(
                    kinesis_stream_arn=stream.stream_arn,
                    role_arn=self.firehose_role.role_arn
                ),
            s3_destination_configuration=
                firehose.CfnDeliveryStream.S3DestinationConfigurationProperty(
                    bucket_arn=self.raw_bucket.bucket_arn,
                    role_arn=self.firehose_role.role_arn,
                    #prefix="cloudevents/collector/!{partitionKey}/year=!{timestamp:yyyy}/month=!{timestamp:MM}/day=!{timestamp:dd}/",
                    #error_output_prefix="cloudevents/error/!{firehose:error-output-type}/year=!{timestamp:yyyy}/month=!{timestamp:MM}/day=!{timestamp:dd}/",
                    buffering_hints=firehose.CfnDeliveryStream.BufferingHintsProperty(
                        interval_in_seconds=60,
                        size_in_m_bs=5
                    ),
                    compression_format="GZIP"
                )
        )
