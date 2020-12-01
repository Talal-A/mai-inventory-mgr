import boto3
import uuid
from . import resources

client = resources.dynamo_client()
TABLE_NAME = 'mai-category'

def get_all_categories():
    result = {}
    response = client.scan(
        TableName = TABLE_NAME,
        AttributesToGet = ['id', 'name']
    )

    for item in response['Items']:
        result[item['id']['S']] = item['name']['S']

    return result

def category_name_exists(category_name):
    category_name = category_name.strip()
    return category_name in get_all_categories().values()

def category_id_exists(category_id):
    response = client.get_item(
        TableName = TABLE_NAME,
        Key = {
            'id': {
                'S': category_id
            }
        }
    )
    return 'Item' in response

def get_category_for_id(category_id):
    response = client.get_item(
        TableName = TABLE_NAME,
        Key = {
            'id': {
                'S': category_id
            }
        }
    )
    return response['Item']['name']['S']

def insert_category(category_name):
    category_name = category_name.strip()
    category_id = str(uuid.uuid4())

    if category_name_exists(category_name) or category_id_exists(category_id):
        print("Error: the name or id already exists!")
        return False

    response = client.put_item(
        TableName = TABLE_NAME,
        Item = {
            'id': {
                'S': category_id
            },
            'name': {
                'S': category_name
            }
        }
    )
    return response is not None

# TODO: Check if any items use this category before deleting!
def delete_category(category_id):
    response = client.delete_item(
        TableName = TABLE_NAME,
        Key = {
            'id': {
                'S': category_id
            }
        }
    )
    return response is not None
