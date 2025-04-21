import os
from aws_cdk import (
    Duration,
    RemovalPolicy,
    Stack,
    aws_kinesis as kinesis,
    aws_iam as iam,
    aws_s3 as s3,
    aws_kinesisfirehose as firehose,
    aws_dynamodb as dynamodb,
    aws_lambda as _lambda,
    aws_sqs as sqs,
    App,
    Environment,
)
from aws_cdk.aws_lambda_event_sources import KinesisEventSource
from constructs import Construct


class EventPipelineStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # 1. Kinesis Stream
        stream = kinesis.Stream(
            self,
            "EventStream",
            retention_period=Duration.hours(24),
            shard_count=1,
            removal_policy=RemovalPolicy.DESTROY,
        )

        # 3. S3 Bucket for raw events
        bucket = s3.Bucket(
            self,
            "RawEventsBucket",
            bucket_name=f"{self.stack_name.lower()}-raw-events",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            lifecycle_rules=[
                s3.LifecycleRule(
                    transitions=[
                        s3.Transition(
                            storage_class=s3.StorageClass.INFREQUENT_ACCESS,
                            transition_after=Duration.days(30),
                        )
                    ],
                    expiration=Duration.days(365),
                )
            ],
            enforce_ssl=True,
        )
        # 4. Firehose Delivery Stream to S3
        fh_role = iam.Role(
            self,
            "FirehoseRole",
            assumed_by=iam.ServicePrincipal("firehose.amazonaws.com"),
        )
        bucket.grant_read_write(fh_role)
        firehose.CfnDeliveryStream(
            self,
            "FirehoseToS3",
            delivery_stream_name=f"{self.stack_name}-fh",
            kinesis_stream_source_configuration=firehose.CfnDeliveryStream.KinesisStreamSourceConfigurationProperty(
                kinesis_stream_arn=stream.stream_arn, role_arn=fh_role.role_arn
            ),
            s3_destination_configuration=firehose.CfnDeliveryStream.S3DestinationConfigurationProperty(
                bucket_arn=bucket.bucket_arn,
                role_arn=fh_role.role_arn,
                prefix="cloudevents/events/year=!{timestamp:yyyy}/month=!{timestamp:MM}/day=!{timestamp:dd}/hour=!{timestamp:HH}/",
                error_output_prefix="cloudevents/errors/!{firehose:random-string}/!{firehose:error-output-type}/year=!{timestamp:yyyy}/month=!{timestamp:MM}/day=!{timestamp:dd}/hour=!{timestamp:HH}/",
                buffering_hints=firehose.CfnDeliveryStream.BufferingHintsProperty(
                    interval_in_seconds=60, size_in_m_bs=128
                ),
                compression_format="GZIP",
            ),
        )

        # 5. DynamoDB Table for lookups
        table = dynamodb.Table(
            self,
            "EventsTable",
            partition_key=dynamodb.Attribute(
                name="application_name", type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="timestamp", type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
        )
        table.add_global_secondary_index(
            index_name="eventIdIndex",
            partition_key=dynamodb.Attribute(
                name="event_id", type=dynamodb.AttributeType.STRING
            ),
            projection_type=dynamodb.ProjectionType.ALL,
        )

        # 6. Lambda to consume Kinesis and write to DynamoDB
        dlq = sqs.Queue(self, "StreamDLQ", retention_period=Duration.days(14))
        lambda_role = iam.Role(
            self,
            "ProcessorRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com")
        )
        table.grant_write_data(lambda_role)

        processor = _lambda.Function(
            self,
            "StreamToDynamoLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="handler.lambda_handler",
            code=_lambda.Code.from_asset("lambda/stream_to_dynamo"),
            role=lambda_role,
            environment={"TABLE_NAME": table.table_name},
            timeout=Duration.minutes(1)
        )
        
        processor.add_event_source(
            KinesisEventSource(
                stream=stream,
                starting_position=_lambda.StartingPosition.LATEST,
                batch_size=100,
                bisect_batch_on_error=True,
                retry_attempts=2,
                report_batch_item_failures=True,
            )
        )

        # 7. Lambda Layer containing event_client
        layer = _lambda.LayerVersion(
            self,
            "EventClientLayer",
            compatible_runtimes=[
                _lambda.Runtime.PYTHON_3_9,
                _lambda.Runtime.PYTHON_3_10,
                _lambda.Runtime.PYTHON_3_12,
                _lambda.Runtime.PYTHON_3_13,
            ],
            code=_lambda.Code.from_asset(os.path.join(os.getcwd(), "lambda/layer")),
            description="Lambda layer with event_client",
        )

        # 8. Producer Lambda using the event_client layer
        # 2. IAM Role for Producers
        producer_role = iam.Role(
            self,
            "ProducerRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
        )
        producer_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "kinesis:PutRecord",
                    "kinesis:PutRecords",
                    "kinesis:DescribeStream",
                    "kinesis:GetShardIterator",
                    "kinesis:GetRecords",
                ],
                resources=[stream.stream_arn],
            )
        )

        producer_fn = _lambda.Function(
            self,
            "ProducerLambda",
            runtime=_lambda.Runtime.PYTHON_3_13,
            handler="handler.lambda_handler",
            code=_lambda.Code.from_asset("lambda/producer"),
            layers=[layer],
            role=producer_role,
            environment={
                "EVENT_STREAM_NAME": stream.stream_name,
                "APPLICATION_NAME": "producer_lambda",
                "EVENT_TYPE": "com.mycompany.producer.event",
            },
            timeout=Duration.seconds(30),
        )


# ─── bootstrap the app ───────────────────────────────────────────────────
app = App()
env = Environment(
    account=os.getenv("CDK_DEFAULT_ACCOUNT"), region=os.getenv("CDK_DEFAULT_REGION")
)
EventPipelineStack(app, "EventPipelineStack", env=env)
app.synth()
