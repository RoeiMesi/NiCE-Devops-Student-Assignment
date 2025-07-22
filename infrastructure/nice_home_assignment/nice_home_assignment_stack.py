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
        
        # Now we will define the lambda function to list all of the objects within the bucket and publish message to the SNS topic.
        list_fn = _lambda.Function(self, "ListObjectsFunctions",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=_lambda.Code.from_asset("../lambda/list_objects"),
            role=role,
            timeout=Duration.seconds(30),
            environment={
                "BUCKET_NAME": bucket.bucket_name
            }
        )
                
        list_fn.add_environment("SNS_TOPIC_ARN", topic.topic_arn)