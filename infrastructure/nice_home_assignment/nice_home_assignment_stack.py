from aws_cdk import (
    Duration,
    Stack,
    CfnParameter,
    aws_s3 as s3,
    aws_lambda as _lambda,
    aws_sns as sns,
    RemovalPolicy,
    aws_s3_deployment as s3deploy,
    aws_iam as iam,
    aws_sns_subscriptions as subscriptions,
    aws_cloudwatch as cw,
)
from constructs import Construct

class NiceHomeAssignmentStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        email_param = CfnParameter(
            self,
            "NotificationEmail",
            type="String",
            description="E-mail address that will receive SNS notifications"
        )
        
        max_keys_param = CfnParameter(self, "MaxKeysPerInvocation",
            type="Number",
            default=1000,
            description="Maximum S3 keys to list per Lambda invocation"
        )
        
        safe_margin_param = CfnParameter(self, "SafeRemainingTimeMs",
            type="Number",
            default=5000,
            description="Milliseconds of buffer before Lambda timeout to stop work"
        )
        
        bucket = s3.Bucket(self, "MyBucket",
            bucket_name="nice-home-task-bucket",
            versioned=True,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )
        
        sample_files_path = "../sample_files"
        s3deploy.BucketDeployment(self, "DeployFiles",
            sources=[s3deploy.Source.asset(sample_files_path)],
            destination_bucket=bucket
        )

        # Create the sns topic.        
        topic = sns.Topic(self, "ExecutionTopic",
            display_name="BucketListerExecutionTopic",
            topic_name="BucketListerExecution")

        # Subscribe an email endpoint to the SNS topic
        topic.add_subscription(
            subscriptions.EmailSubscription(email_param.value_as_string)
        )

        # Defining the IAM role with least privilege permissions:
        role = iam.Role(self, "ListerRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com")
        )
        
        # Add S3 read access policy
        role.add_to_policy(iam.PolicyStatement(
            actions=["s3:GetBucket", "s3:ListBucket", "s3:GetObject"],
            resources=[bucket.bucket_arn, bucket.arn_for_objects("*")] 
        ))
        
        # Add SNS publish access
        role.add_to_policy(iam.PolicyStatement(
            actions=["sns:Publish"],
            resources=[topic.topic_arn]
        ))
        
        # Add lambda execution
        role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
        )
        
        # Define the lambda function to list all of the objects within the bucket and publish message to the SNS topic.
        list_fn = _lambda.Function(self, "ListObjectsFunctions",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=_lambda.Code.from_asset("../lambda/list_objects"),
            timeout=Duration.seconds(30),
            environment={
                "BUCKET_NAME": bucket.bucket_name,
                "SNS_TOPIC_ARN": topic.topic_arn,
                "MAX_KEYS": max_keys_param.value_as_string,
                "SAFE_MARGIN_MS": safe_margin_param.value_as_string,
            },
            role=role,
        )
        
        cw.Alarm(self, "HighP90Duration",
            metric=list_fn.metric_duration(statistic="p95"),
            threshold=24000,
            evaluation_periods=2,
            comparison_operator=cw.ComparisonOperator.GREATER_THAN_THRESHOLD,
            alarm_description="Alert if 95th-percentile duration > 24s",
        )