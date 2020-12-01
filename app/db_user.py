import boto3
import uuid
from . import resources

client = resources.dynamo_client()
TABLE_NAME = 'mai-user'

def get_all_users():
    result = []
    response = client.scan(
        TableName = TABLE_NAME,
        AttributesToGet = ['id', 'name', 'email', 'role']
    )

    for item in response['Items']:
        current_result = {
            'id': item['id']['S'],
            'name': item['name']['S'],
            'email': item['email']['S'],
            'role': int(item['role']['N']),
        }
        result.append(current_result)

    return result

def user_id_exists(user_id):
    response = client.get_item(
        TableName = TABLE_NAME,
        Key = {
            'id': {
                'S': user_id
            }
        }
    )
    return 'Item' in response

def get_user_for_id(user_id):
    response = client.get_item(
        TableName = TABLE_NAME,
        Key = {
            'id': {
                'S': user_id
            }
        }
    )
    result = {
        'id': response['Item']['id']['S'],
        'name': response['Item']['name']['S'],
        'email': response['Item']['email']['S'],
        'role': int(response['Item']['role']['N']),
    }

    return result

def create_user(user_id, user_name, user_email, user_role):
    response = client.put_item(
        TableName = TABLE_NAME,
        Item = {
            'id': {
                'S': user_id
            },
            'name': {
                'S': user_name
            },
            'email': {
                'S': user_email
            },
            'role': {
                'N': str(user_role)
            },
        }
    )
    return response is not None

def delete_user(user_id):
    response = client.delete_item(
        TableName = TABLE_NAME,
        Key = {
            'id': {
                'S': user_id
            }
        }
    )
    return response is not None
