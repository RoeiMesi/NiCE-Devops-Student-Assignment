import os, json
import boto3
from datetime import datetime

# Defining the client for interacting with the S3 resource.
s3 = boto3.client("s3")
# Defining the client for interacting with the sns resource.
sns = boto3.client("sns")

# Defining the client for interacting with the lambda function resource.
lambda_client = boto3.client("lambda")

# Environment variables
bucket_name = os.environ["BUCKET_NAME"]
topic_arn = os.environ["SNS_TOPIC_ARN"]
max_keys = int(os.environ.get("MAX_KEYS", "1000"))
safe_margin_ms = int(os.environ.get("SAFE_MARGIN_MS", "5000"))
    
def handler(event, context):
    token = event.get("ContinuationToken")
    processed = 0
    sample_keys = []
    
    while True:
        params = {"Bucket": bucket_name, "MaxKeys": max_keys}
        if token:
            params["ContinuationToken"] = token
            
        resp = s3.list_objects_v2(**params)
        contents = resp.get("Contents", [])
        for obj in contents:
            processed += 1
            
            if len(sample_keys) < 10:
                sample_keys.append(obj["Key"])
        token = resp.get("NextContinuationToken")
        
        if not token or context.get_remaining_time_in_millis() < safe_margin_ms:
            break

        # Defining the execution details:
    message = {
        "function": context.function_name,
        "timestamp": context.aws_request_id,
        "bucket": bucket_name,
        "keys": sample_keys,
    }
    
    sns.publish(
        TopicArn=topic_arn,
        Subject="Bucket Lister Execution",
        Message=json.dumps(message)
    )
    
    if token:
        lambda_client.invoke(
            FunctionName=context.function_name,
            InvocationType="Event",
            Payload=json.dumps({"ContinuationToken": token})
        )
        
    return {
        "processed": processed,
        "isTruncated": bool(token),
        "nextToken": token
    }
