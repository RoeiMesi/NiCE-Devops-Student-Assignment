from aws_cdk import (
    Duration,
    Stack,
    CfnParameter,
    aws_s3 as s3,
    aws_lambda as _lambda,
    # aws_sqs as sqs,
)
from constructs import Construct

class NiceHomeAssignmentStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        bucket_name_param = CfnParameter(self, "BucketName", type="String",
            description="The S3 bucket whose objects we will list"
        )
        
        # Now when we have the name of the bucket, we will import it using the aws s3 module:
        bucket = s3.Bucket.from_bucket_name(self, "ImportedBucket",
            bucket_name_param.value_as_string
        )
        
        # Now we will define the lambda function to list all of the objects within the bucket:
        list_fn = _lambda.Function(self, "ListObjectsFunctions",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=_lambda.Code.from_asset("lambda/list_objects"),
            timeout=Duration.seconds(30),
            environment={
                "BUCKET_NAME": bucket.bucket_name
            }
        )
        bucket.grant_read(list_fn)