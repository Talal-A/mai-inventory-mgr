import boto3
from . import resources

client = resources.dynamo_client()
TABLE_NAME = 'mai-barcode'

def barcode_exists(barcode):
    response = client.get_item(
        TableName = TABLE_NAME,
        Key = {
            'barcode': {
                'S': barcode
            }
        }
    )
    return 'Item' in response

def get_item_id_for_barcode(barcode):
    response = client.get_item(
        TableName = TABLE_NAME,
        Key = {
            'barcode': {
                'S': barcode
            }
        }
    )
    return response['Item']['item_id']['S']

def insert_barcode(barcode, item_id):
    if barcode_exists(barcode):
        print("Error: the barcode already exists!")
        return False

    response = client.put_item(
        TableName = TABLE_NAME,
        Item = {
            'barcode': {
                'S': barcode
            },
            'item_id': {
                'S': item_id
            }
        }
    )
    return response is not None

def delete_barcode(barcode):
    response = client.delete_item(
        TableName = TABLE_NAME,
        Key = {
            'barcode': {
                'S': barcode
            }
        }
    )
    return response is not None
