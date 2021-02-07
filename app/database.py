import sqlite3
import json 
import uuid
from datetime import datetime
from flask import request

DB_PATH = '/data/mai.db'

# To be called ONCE from application startup
def __init_db():
    db_connection = sqlite3.connect(DB_PATH)
    __check_table(db_connection)

def __get_db():
    db_connection = sqlite3.connect(DB_PATH)
    db_connection.execute('pragma journal_mode=wal')
    return db_connection

def __check_table(db_connection):
    cursor = db_connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS barcode (
            barcode text, item_id text, 
            UNIQUE(barcode)
        )
        """
    )
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS category (
            category_id text, name text,
            UNIQUE(category_id)
        )
        """
    )
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            date int, type text, user text, event text
        )
        """
    )

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS item (
            item_id text, category_id text, name text, location text, quantity_active int, quantity_expired int, notes text, url text,
            UNIQUE(item_id)
        )
        """
    )

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user (
            user_id text, user_name text, user_email text, user_role int,
            UNIQUE(user_id)
        )
        """
    )

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS image (
            image_id text, image_url text, deletion_hash text, item_id text,
            UNIQUE(image_id)
        )
        """
    )

    db_connection.commit()
    cursor.close()

####################
# HELPER FUNCTIONS #
####################

# Format a timestamp into a string
def __format_timestamp(time):
    dt_object = datetime.fromtimestamp(time)
    return dt_object.strftime('%d-%b-%Y %H:%M:%S')    

#####################
# BARCODE FUNCTIONS #
#####################

# Insert a new barcode
def insert_barcode(barcode, item_id):
    db_connection = __get_db()
    cursor = db_connection.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO barcode (barcode, item_id)
        VALUES(?, ?)""", (
            str(barcode).strip(),
            str(item_id)
        ))
    
    # Save (commit) the changes
    db_connection.commit()
    cursor.close()

# Return true if barcode already exists
def exists_barcode(barcode):
    cursor = __get_db().cursor()

    query_result = cursor.execute("""
        SELECT EXISTS(SELECT 1 FROM barcode WHERE barcode=? LIMIT 1)""", (
            str(barcode).strip(),
    ))
    
    for row in query_result:
        exists = (row[0] == 1)
        cursor.close()
        return exists

# Get item_id associated with a given barcode
def get_barcode(barcode):
    result = None
    cursor = __get_db().cursor()

    query_results = cursor.execute("""
        SELECT * FROM barcode WHERE barcode=?""", (
            str(barcode).strip(),
    ))

    for row in query_results:
        result = {
            'barcode': str(row[0]),
            'item_id': str(row[1])
        }

    cursor.close()
    return result

# Return all barcodes associated with an item_id
def get_barcodes_for_item(item_id):
    result = []
    cursor = __get_db().cursor()

    query_results = cursor.execute("""
        SELECT * FROM barcode WHERE item_id=? """, (
            str(item_id),
    ))

    for row in query_results:
        result.append({
            'barcode': str(row[0]),
            'item_id': str(row[1])
        })

    cursor.close()
    return result

# Return all barcodes
def get_all_barcodes():
    result = []
    cursor = __get_db().cursor()

    query_results = cursor.execute("""
        SELECT * FROM barcode"""
    )

    for row in query_results:
        result.append({
            'barcode': str(row[0]),
            'item_id': str(row[1]),
            'item_name': get_item(str(row[1]))['name']
        })

    cursor.close()
    return result

# Delete a single barcode
def delete_barcode(barcode):
    db_connection = __get_db()
    cursor = db_connection.cursor()

    query_results = cursor.execute("""
        DELETE FROM barcode WHERE barcode=?""", (
            str(barcode).strip(),
    ))

    db_connection.commit()
    cursor.close()

# Delete all barcodes associated with an item_id
def delete_barcodes_for_item(item_id):
    db_connection = __get_db()
    cursor = db_connection.cursor()

    query_results = cursor.execute("""
        DELETE FROM barcode WHERE item_id=?""", (
            str(item_id),
    ))

    db_connection.commit()
    cursor.close()

#####################
# HISTORY FUNCTIONS #
#####################

# Get user if authenticated, otherwise fall back to ip address
def __get_user(user):
    username = ""
    if user.is_authenticated:
        username = user.email
    else:
        ip_address = ""
        if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
            ip_address = str(request.environ['REMOTE_ADDR'])
        else:
            ip_address = str(request.environ['HTTP_X_FORWARDED_FOR']) # if behind a proxy
        username = "guest - " + ip_address

    return username

# Insert a new history event
def insert_history(type, user, event):
    db_connection = __get_db()
    cursor = db_connection.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO history (date, type, user, event)
        VALUES(?, ?, ?, ?)""", (
            datetime.now().timestamp(), 
            str(type), 
            str(__get_user(user)), 
            str(event)
        ))
    
    # Save (commit) the changes
    db_connection.commit()
    cursor.close()

# Get all history events
def get_history():
    result = []
    cursor = __get_db().cursor()

    query_results = cursor.execute("""
        SELECT * FROM history ORDER BY date DESC"""
    )

    for row in query_results:
        result.append({
            'date_raw': int(row[0]),
            'date': __format_timestamp(int(row[0])),
            'type': str(row[1]),
            'user': str(row[2]),
            'event': str(row[3])
        })
    cursor.close()
    return result

######################
# CATEGORY FUNCTIONS #
######################

# Insert a new category
def insert_category(category_name):
    category_id = str(uuid.uuid4())

    db_connection = __get_db()
    cursor = db_connection.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO category (category_id, name)
        VALUES(?, ?)""", (
            str(category_id).strip(),
            str(category_name).strip()
        ))

    db_connection.commit()
    cursor.close()

# Return true if a category with the same name already exists
def exists_category_name(category_name):
    cursor = __get_db().cursor()

    query_result = cursor.execute("""
        SELECT EXISTS(SELECT 1 FROM category WHERE name=? LIMIT 1)""", (
            str(category_name).strip(),
    ))
    
    for row in query_result:
        exists = (row[0] == 1)
        cursor.close()
        return exists

# Return true if the category id already exists
def exists_category_id(category_id):
    cursor = __get_db().cursor()

    query_result = cursor.execute("""
        SELECT EXISTS(SELECT 1 FROM category WHERE category_id=? LIMIT 1)""", (
            str(category_id).strip(),
    ))
    
    for row in query_result:
        exists = (row[0] == 1)
        cursor.close()
        return exists

# Return true if category is actively used by an item
def exists_category_usage(category_id):
    cursor = __get_db().cursor()

    query_result = cursor.execute("""
        SELECT EXISTS(SELECT 1 FROM item WHERE category_id=? LIMIT 1)""", (
            str(category_id).strip(),
    ))
    
    for row in query_result:
        exists = (row[0] == 1)
        cursor.close()
        return exists

# Get a category for a given category_id
def get_category(category_id):
    result = None
    cursor = __get_db().cursor()

    query_results = cursor.execute("""
        SELECT * FROM category WHERE category_id=?""", (
            str(category_id).strip(),
    ))

    for row in query_results:
        result = {
            'id': str(row[0]),
            'name': str(row[1])
        }

    cursor.close()
    return result

# Get all categories
def get_all_categories():
    result = []
    cursor = __get_db().cursor()

    query_results = cursor.execute("""
        SELECT * FROM category""", (
    ))

    for row in query_results:
        result.append({
            'id': str(row[0]),
            'name': str(row[1])
        })

    cursor.close()
    return result

# Get all categories which can be deleted safely (not referenced by any items)
def get_deletable_categories():
    all_categories = get_all_categories()
    deletable_categories = []
    for category in all_categories:
        if not exists_category_usage(category['id']):
            deletable_categories.append(category)
    return deletable_categories

# Update the name for a given category_id
def update_category_name(category_id, new_name):
    db_connection = __get_db()
    cursor = db_connection.cursor()

    cursor.execute("""
        UPDATE category SET name=? WHERE category_id=?""", (
            str(new_name).strip(),
            str(category_id).strip()
        ))
    
    # Save (commit) the changes
    db_connection.commit()
    cursor.close()

# Delete a category for a given category_id
def delete_category(category_id):
    if exists_category_usage(category_id):
        # Cannot delete an actively used category
        return 
    
    db_connection = __get_db()
    cursor = db_connection.cursor()

    query_results = cursor.execute("""
        DELETE FROM category WHERE category_id=?""", (
            str(category_id).strip(),
    ))

    db_connection.commit()
    cursor.close()

###################
# USER FUNCTIONS #
###################

# Insert a new user
def insert_user(user_id, user_name, user_email, user_role):
    db_connection = __get_db()
    cursor = db_connection.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO user (user_id, user_name, user_email, user_role)
        VALUES(?, ?, ?, ?)""", (
            str(user_id).strip(),
            str(user_name).strip(),
            str(user_email).strip(),
            int(user_role)
        ))
    
    # Save (commit) the changes
    db_connection.commit()
    cursor.close()

# Return true if user id already exists
def exists_user_id(user_id):
    cursor = __get_db().cursor()

    query_result = cursor.execute("""
        SELECT EXISTS(SELECT 1 FROM user WHERE user_id=? LIMIT 1)""", (
            str(user_id).strip(),
    ))
    
    for row in query_result:
        exists = (row[0] == 1)
        cursor.close()
        return exists

# Get a user for a given user_id
def get_user(user_id):
    result = None
    cursor = __get_db().cursor()

    query_results = cursor.execute("""
        SELECT * FROM user WHERE user_id=?""", (
            str(user_id).strip(),
    ))

    for row in query_results:
        result = {
            'user_id': str(row[0]),
            'user_name': str(row[1]),
            'user_email': str(row[2]),
            'user_role': int(row[3])
        }

    cursor.close()
    return result

# Get all users
def get_all_users():
    result = []
    cursor = __get_db().cursor()

    query_results = cursor.execute("""
        SELECT * FROM user""", (
    ))

    for row in query_results:
        result.append({
            'user_id': str(row[0]),
            'user_name': str(row[1]),
            'user_email': str(row[2]),
            'user_role': int(row[3])
        })

    cursor.close()
    return result

# Update the role for a given user_id
def update_user_role(user_id, new_role):
    db_connection = __get_db()
    cursor = db_connection.cursor()

    cursor.execute("""
        UPDATE user SET user_role=? WHERE user_id=?""", (
            int(new_role),
            str(user_id).strip()
        ))
    
    # Save (commit) the changes
    db_connection.commit()
    cursor.close()

# Delete a user for a given user_id
def delete_user(user_id):
    db_connection = __get_db()
    cursor = db_connection.cursor()

    query_results = cursor.execute("""
        DELETE FROM user WHERE user_id=?""", (
            str(user_id).strip(),
    ))

    db_connection.commit()
    cursor.close()

##################
# ITEM FUNCTIONS #
##################

# Insert an item
def insert_item(category_id, name, location="", quantity_active=0, quantity_expired=0, notes="", url=""):
    item_id = str(uuid.uuid4())

    db_connection = __get_db()
    cursor = db_connection.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO item (item_id, category_id, name, location, quantity_active, quantity_expired, notes, url)
        VALUES(?, ?, ?, ?, ?, ?, ?, ?)""", (
            str(item_id).strip(),
            str(category_id).strip(),
            str(name).strip(),
            str(location).strip(),
            int(quantity_active),
            int(quantity_expired),
            str(notes),
            str(url).strip()
        ))

    db_connection.commit()
    cursor.close()

# Return true if item_id already exists
def exists_item_id(item_id):
    cursor = __get_db().cursor()

    query_result = cursor.execute("""
        SELECT EXISTS(SELECT 1 FROM item WHERE item_id=? LIMIT 1)""", (
            str(item_id).strip(),
    ))
    
    for row in query_result:
        exists = (row[0] == 1)
        cursor.close()
        return exists

# Get an item for a given item_id
def get_item(item_id):
    result = None
    cursor = __get_db().cursor()

    query_results = cursor.execute("""
        SELECT * FROM item WHERE item_id=?""", (
            str(item_id).strip(),
    ))

    for row in query_results:
        result = {
            'id': str(row[0]),
            'category_id': str(row[1]),
            'category_name': get_category(str(row[1]))['name'],
            'name': str(row[2]),
            'location': str(row[3]),
            'quantity_active': int(row[4]),
            'quantity_expired': int(row[5]),
            'notes': str(row[6]),
            'url': str(row[7])
        }

    cursor.close()
    return result

# Get all items
def get_all_items():
    result = []
    cursor = __get_db().cursor()
    
    # # Cache list of categories
    cached_categories = {}
    for category in get_all_categories():
        cached_categories[category['id']] = category['name']

    query_results = cursor.execute("""
        SELECT * FROM item""", (
    ))

    for row in query_results:
        result.append({
            'id': str(row[0]),
            'category_id': str(row[1]),
            'category_name': cached_categories[str(row[1])],
            'name': str(row[2]),
            'location': str(row[3]),
            'quantity_active': int(row[4]),
            'quantity_expired': int(row[5]),
            'notes': str(row[6]),
            'url': str(row[7])
        })

    cursor.close()
    return result

# Get all items under a given category
def get_all_items_for_category(category_id):
    result = []
    cursor = __get_db().cursor()

    # Cache category name
    cached_category_name = get_category(str(category_id).strip())['name']

    query_results = cursor.execute("""
        SELECT * FROM item WHERE category_id=?""", (
            str(category_id).strip(),
    ))

    for row in query_results:
        result.append({
            'id': str(row[0]),
            'category_id': str(row[1]),
            'category_name': cached_category_name,
            'name': str(row[2]),
            'location': str(row[3]),
            'quantity_active': int(row[4]),
            'quantity_expired': int(row[5]),
            'notes': str(row[6]),
            'url': str(row[7])
        })

    cursor.close()
    return result

# Update an item with new values
def update_item(item_id, category_id, location, quantity_active, quantity_expired, notes, url):
    db_connection = __get_db()
    cursor = db_connection.cursor()

    cursor.execute("""
        UPDATE item SET category_id=?, location=?, quantity_active=?, quantity_expired=?, notes=?, url=? WHERE item_id=?""", (
            str(category_id).strip(),
            str(location).strip(),
            int(quantity_active),
            int(quantity_expired),
            str(notes),
            str(url).strip(),
            str(item_id).strip()
        ))
    
    # Save (commit) the changes
    db_connection.commit()
    cursor.close()

# Update an item's active quantity
def update_item_quantity(item_id, new_active_quantity):
    db_connection = __get_db()
    cursor = db_connection.cursor()

    cursor.execute("""
        UPDATE item SET quantity_active=? WHERE item_id=?""", (
            int(new_active_quantity),
            str(item_id).strip()
        ))
    
    # Save (commit) the changes
    db_connection.commit()
    cursor.close()

# Delete an item for a given item_id
def delete_item(item_id):
    db_connection = __get_db()
    cursor = db_connection.cursor()

    query_results = cursor.execute("""
        DELETE FROM item WHERE item_id=?""", (
            str(item_id).strip(),
    ))

    db_connection.commit()
    cursor.close()

    delete_barcodes_for_item(item_id)

##################
# SCAN FUNCTIONS #
##################

# Safely update quantity for an item, using a barcode
def scan_barcode_update_quantity(barcode_id, diff):
    barcode = get_barcode(barcode_id)
    if barcode == None:
        return False
    item = get_item(barcode['item_id'])
    if item == None:
        return False
    else:
        new_quantity = item['quantity_active']
        new_quantity += diff
        if new_quantity < 0:
            return False
        else:
            # Perform update and return true
            update_item_quantity(item['id'], new_quantity)
            return True

# Safely update quantity for an item
def search_item_update_quantity(item_id, diff):
    item = get_item(item_id)
    if item == None:
        return False
    else:
        new_quantity = item['quantity_active']
        new_quantity += diff
        if new_quantity < 0:
            return False
        else:
            # Perform update and return true
            update_item_quantity(item['id'], new_quantity)
            return True

###################
# IMAGE FUNCTIONS #
###################

# Insert an image
def insert_image(image_url, deletion_hash, item_id):
    image_id = str(uuid.uuid4())

    db_connection = __get_db()
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

# Return true if image_id already exists
def exists_item_id(image_id):
    cursor = __get_db().cursor()

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
    cursor = __get_db().cursor()

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
    cursor = __get_db().cursor()
    
    query_results = cursor.execute("""
        SELECT * FROM image""", (
    ))

    for row in query_results:
        result.append({
            'image_id': str(row[0]),
            'image_url': str(row[1]),
            'deletion_hash': str(row[2]),
            'item_id': str(row[3]),
            'item_name': get_item(str(row[3]))['name']
        })

    cursor.close()
    return result

# Get all images for an item
def get_all_images_for_item(item_id):
    result = []
    cursor = __get_db().cursor()

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
def delete_item(image_id):
    db_connection = __get_db()
    cursor = db_connection.cursor()

    query_results = cursor.execute("""
        DELETE FROM image WHERE image_id=?""", (
            str(image_id).strip(),
    ))

    db_connection.commit()
    cursor.close()

# Delete all images for a given item_id
def delete_images_for_item(item_id):
    db_connection = __get_db()
    cursor = db_connection.cursor()

    query_results = cursor.execute("""
        DELETE FROM image WHERE item_id=?""", (
            str(item_id).strip(),
    ))

    db_connection.commit()
    cursor.close()