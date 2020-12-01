import boto3
import uuid
from datetime import datetime
from flask import request
from . import resources

client = resources.dynamo_client()
TABLE_NAME = 'mai-history'

def __isoformat_current_time():
    return datetime.utcnow().replace(microsecond=0).isoformat()

def __format_timestamp(time):
    dt_object = datetime.fromtimestamp(time)
    return dt_object.strftime('%H:%M:%S on %m/%d/%y')    

def __get_username(user):
    username = ""
    if user.is_authenticated:
        username = user.email
    else:
        ipAddress = ""
        if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
            ipAddress = str(request.environ['REMOTE_ADDR'])
        else:
            ipAddress = str(request.environ['HTTP_X_FORWARDED_FOR']) # if behind a proxy
        username = "guest - " + ipAddress
    return username

def insert_history(type, user, event):
    response = client.put_item(
        TableName = TABLE_NAME,
        Item = {
            'id': {
                'S': str(uuid.uuid4())
            },
            'time': {
                'S': __isoformat_current_time()
            },
            'type': {
                'S': type
            },
            'user': {
                'S': __get_username(user)
            },
            'event': {
                'S': event
            },
        }
    )
    return response is not None

def get_history():
    result = []
    response = client.scan(
        TableName = TABLE_NAME,
        AttributesToGet = ['id', 'time', 'event', 'user', 'type'],
    )

    for item in response['Items']:
        current_result = {
            'id': item['id']['S'],
            'time': item['time']['S'],
            'event': item['event']['S'],
            'user': item['user']['S'],
            'type': item['type']['S'],
        }
        result.append(current_result)

    # Sort the results by time. Newest items first.
    result.sort(key = lambda x: x['time'], reverse = True)
    return result
