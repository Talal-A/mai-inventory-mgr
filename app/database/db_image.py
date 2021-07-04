import uuid
import requests
import config

from . import db_util as db
from . import db_item, db_audit


###################
# IMAGE FUNCTIONS #
###################

# Insert an image
def insert_image(image_url, deletion_hash, item_id):
    image_id = str(uuid.uuid4())

    db_connection = db.get_data_db()
    cursor = db_connection.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO image (image_id, image_url, deletion_hash, item_id)
        VALUES(?, ?, ?, ?)""", (
            str(image_id).strip(),
            str(image_url).strip(),
            str(deletion_hash).strip(),
            str(item_id).strip()
        ))

    db_connection.commit()
    cursor.close()

    db_audit.insert_item_audit_event(item_id, "Added image.", "", get_image(image_id))

# Return true if image_id already exists
def exists_item_id(image_id):
    cursor = db.get_data_db().cursor()

    query_result = cursor.execute("""
        SELECT EXISTS(SELECT 1 FROM image WHERE image_id=? LIMIT 1)""", (
            str(image_id).strip(),
    ))
    
    for row in query_result:
        exists = (row[0] == 1)
        cursor.close()
        return exists

# Get an image for a given image_id
def get_image(image_id):
    result = None
    cursor = db.get_data_db().cursor()

    query_results = cursor.execute("""
        SELECT * FROM image WHERE image_id=?""", (
            str(image_id).strip(),
    ))

    for row in query_results:
        result = {
            'image_id': str(row[0]),
            'image_url': str(row[1]),
            'deletion_hash': str(row[2]),
            'item_id': str(row[3])
        }

    cursor.close()
    return result

# Get all images
def get_all_images():
    result = []
    cursor = db.get_data_db().cursor()
    
    query_results = cursor.execute("""
        SELECT * FROM image""", (
    ))

    for row in query_results:
        result.append({
            'image_id': str(row[0]),
            'image_url': str(row[1]),
            'deletion_hash': str(row[2]),
            'item_id': str(row[3]),
            'item_name': db_item.get_item(str(row[3]))['name']
        })

    cursor.close()
    return result

# Get all images for an item
def get_all_images_for_item(item_id):
    result = []
    cursor = db.get_data_db().cursor()

    query_results = cursor.execute("""
        SELECT * FROM image WHERE item_id=?""", (
            str(item_id).strip(),
    ))

    for row in query_results:
        result.append({
            'image_id': str(row[0]),
            'image_url': str(row[1]),
            'deletion_hash': str(row[2]),
            'item_id': str(row[3])
        })

    cursor.close()
    return result

# Delete an image for a given image_id
def delete_image(image_id):
    image = get_image(image_id)
    
    if __delete_image_from_imgur(image['deletion_hash']):
        db_connection = db.get_data_db()
        cursor = db_connection.cursor()

        query_results = cursor.execute("""
            DELETE FROM image WHERE image_id=?""", (
                str(image_id).strip(),
        ))

        db_connection.commit()
        cursor.close()

        db_audit.insert_item_audit_event(image['item_id'], "Deleted image.", image, "")

# Delete all images for a given item_id
def delete_images_for_item(item_id):
    for image in get_all_images_for_item(item_id):
        delete_image(image['image_id'])

# Delete an image from the imgur api
def __delete_image_from_imgur(deletion_hash):
    try:
        result = requests.delete(
            url='https://api.imgur.com/3/image/' + str(deletion_hash),
            headers={'Authorization': 'Client-ID ' + config.IMGUR_CLIENT_ID}
            ).json()
        success = result['success']
        return success
    except:
        return False
