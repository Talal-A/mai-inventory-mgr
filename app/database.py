import sqlite3
import json 
from datetime import datetime
from flask import request

DB_PATH = './data/mai.db'

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
            'item_id': str(row[1])
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
def insert_category():
    return None

# Return true if a category with the same name already exists
def exists_category_name():
    return None

# Return true if the category id already exists
def exists_category_id():
    return None

# Get a category for a given category_id
def get_category():
    return None

# Get all categories
def get_all_categories():
    return None

# Delete a category for a given category_id
# TODO: Only delete if no items are actively using this category_id
def delete_category():
    return None

###################
# USER FUNCTIONS #
###################

# Insert a new user
def insert_user():
    return None

# Return true if user id already exists
def exists_user_id():
    return None

# Get a user for a given user_id
def get_user():
    return None

# Get all users
def get_all_users():
    return None

# Update the role for a given user_id
def update_user_role():
    return None

# Delete a user for a given user_id
def delete_user():
    return None

##################
# ITEM FUNCTIONS #
##################

# Insert an item
def insert_item():
    return None

# Return true if item_id already exists
def exists_item_id():
    return None

# Get an item for a given item_id
def get_item():
    return None

# Get all items
def get_all_items():
    return None

# Update an item with new values
def update_item():
    return None

# Delete an item for a given item_id
# TODO: Delete barcodes associated with item
def delete_item():
    return None