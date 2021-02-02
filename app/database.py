import sqlite3
import json 
from datetime import datetime

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

#####################
# BARCODE FUNCTIONS #
#####################

# Insert a new barcode
def insert_barcode():
    return None

# Get item_id associated with a given barcode
def get_barcode():
    return None

# Return all barcodes associated with an item_id
def get_barcodes_for_item():
    return None

# Return all barcodes
def get_all_barcodes():
    return None

# Delete a single barcode
def delete_barcode():
    return None

# Delete all barcodes associated with an item_id
def delete_barcodes_for_item():
    return None

#####################
# HISTORY FUNCTIONS #
#####################

# Insert a new history event
def insert_history():
    return None

# Get all history events
def get_history():
    return None

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