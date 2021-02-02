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

