import os
import boto3

def handler(event, context):
    bucket_name = os.environ["BUCKET_NAME"]
    client = boto3.client("s3")
    resp = client.list_objects_v2(Bucket=bucket_name)
    return {
        "objects": [obj["Key"] for obj in resp.get("Contents", [])]
    }