import boto3
import os

AWS_ACCESS_KEY = os.environ.get("MAI_AWS_ACCESS_KEY_ID", None)
AWS_SECRET_KEY = os.environ.get("MAI_AWS_SECRET_ACCESS_KEY", None)

def dynamo_client():
    client = boto3.client(
        'dynamodb', 
        region_name='us-west-1',
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY)
    return client