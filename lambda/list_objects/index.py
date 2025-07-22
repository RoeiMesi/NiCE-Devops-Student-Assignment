import os, json
import boto3
from datetime import datetime

# Defining the client for interacting with the S3 resource.
s3 = boto3.client("s3")
# Defining the client for interacting with the sns resource.
sns = boto3.client("sns")

def handler(event, context):
    bucket_name = os.environ["BUCKET_NAME"]
    topic_arn = os.environ["SNS_TOPIC_ARN"]
    
    resp = s3.list_objects_v2(Bucket=bucket_name)
    keys = [obj["Key"] for obj in resp.get("Contents", [])]
    
    # Defining the execution details:
    message = {
        "function": context.function_name,
        "timestamp": datetime.utcnow().isoformat()+"Z",
        "bucket": bucket_name,
        "object_count": len(keys),
        "keys": keys
    }
    
    sns.publish(
        TopicArn=topic_arn,
        Subject="Bucket Lister Execution",
        Message=json.dumps(message)
    )
    
    objects_dict = {"objects": keys}
    
    return objects_dict