from aws_cdk import (
    Duration,
    Stack,
    CfnParameter,
    aws_s3 as s3,
    aws_lambda as _lambda,
    aws_sns as sns,
    RemovalPolicy,
    aws_s3_deployment as s3deploy
)
from constructs import Construct

class NiceHomeAssignmentStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
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
        
        # Now we will define the lambda function to list all of the objects within the bucket:
        list_fn = _lambda.Function(self, "ListObjectsFunctions",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=_lambda.Code.from_asset("../lambda/list_objects"),
            timeout=Duration.seconds(30),
            environment={
                "BUCKET_NAME": bucket.bucket_name
            }
        )
        
        topic = sns.Topic(self, "ExecutionTopic", display_name="BucketListerExecutionTopic", topic_name="BucketListerExecution")
        
        bucket.grant_read(list_fn)
        topic.grant_publish(list_fn)
        list_fn.add_environment("SNS_TOPIC_ARN", topic.topic_arn)