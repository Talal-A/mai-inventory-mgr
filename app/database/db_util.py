import sqlite3
from datetime import datetime

DB_PATH = '/data/mai.db'
DB_NAME = 'mai-db'
DB_VERSION = 1

##################
# CORE FUNCTIONS #
##################

# Initializes the database. To be called ONCE from application startup
def init_db():
    db_connection = sqlite3.connect(DB_PATH)
    __check_table(db_connection)
    __upgrade_db(db_connection)

def get_db():
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

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS version (
            db_name text, db_version int,
            UNIQUE(db_name)
        )"""
    )

    cursor.execute("""
        INSERT OR IGNORE INTO version (db_name, db_version)
        VALUES(?, ?)""", (
            DB_NAME,
            DB_VERSION
    ))

    db_connection.commit()
    cursor.close()

def __upgrade_db(db_connection):
    current_version = -1
    cursor = db_connection.cursor()

    # Get current db version
    query_results = cursor.execute("""
        SELECT db_version FROM version WHERE db_name=?""", (
            str(DB_NAME),
    ))

    for row in query_results:
        current_version = int(row[0])

    print("Latest database version: " + str(current_version))
    print("Expected database version: " + str(DB_VERSION))

    if current_version == -1:
        raise Exception("Error: was not able to pull the current db version")
    
    if current_version == DB_VERSION:
        return

    # Finally, commit the changes and close the cursor.
    db_connection.commit()
    cursor.close()

####################
# HELPER FUNCTIONS #
####################

# Format a timestamp into a string
def format_timestamp(time):
    dt_object = datetime.fromtimestamp(time)
    return dt_object.strftime('%d-%b-%Y %H:%M:%S')    