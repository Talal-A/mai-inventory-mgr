import sqlite3
from datetime import datetime
from flask import request
import logging

DATA_DB_PATH = './data/mai.db'
DATA_DB_NAME = 'mai-db'
DATA_DB_VERSION = 4

LOG_DB_PATH = './data/mai-log.db'
LOG_DB_NAME = 'mai-logs'
LOG_DB_VERSION = 0

##################
# CORE FUNCTIONS #
##################

# Initializes the database. To be called ONCE from application startup
def init_db():
    __init_data_db()
    __init_log_db()

#####################
# DATA DB FUNCTIONS #
#####################

def __init_data_db():
    db_connection = sqlite3.connect(DATA_DB_PATH)
    __check_data_table(db_connection)
    __upgrade_data_db(db_connection)

def get_data_db():
    db_connection = sqlite3.connect(DATA_DB_PATH)
    db_connection.execute('pragma journal_mode=wal')
    return db_connection

def __check_data_table(db_connection):
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
            item_id text, category_id text, name text, location text, quantity_active int, quantity_expired int, notes text, url text, deleted int,
            UNIQUE(item_id)
        )
        """
    )

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user (
            user_id text, user_name text, user_email text, user_role int, user_picture text,
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
        CREATE TABLE IF NOT EXISTS audit (
            date int, type text, id text, user text, event text, before text, after text
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
            DATA_DB_NAME,
            DATA_DB_VERSION
    ))

    db_connection.commit()
    cursor.close()

def __upgrade_data_db(db_connection):
    current_version = -1
    cursor = db_connection.cursor()

    # Get current db version
    query_results = cursor.execute("""
        SELECT db_version FROM version WHERE db_name=?""", (
            str(DATA_DB_NAME),
    ))

    for row in query_results:
        current_version = int(row[0])

    logging.info("Latest data database version: " + str(current_version))
    logging.info("Expected data database version: " + str(DATA_DB_VERSION))

    if current_version == -1:
        raise Exception("Error: was not able to pull the current db version")
    
    if current_version == DATA_DB_VERSION:
        logging.info("No data database update is needed.")
        return

    if current_version < 2:
        # Upgrade to v2.0
        logging.info("Upgrading data database to 2.0")

        cursor.execute("""
            ALTER TABLE user ADD COLUMN user_picture text DEFAULT '/static/mai_logo.png'
        
        """)
    
        cursor.execute("""
            INSERT OR REPLACE INTO version (db_name, db_version)
            VALUES(?, ?)""", (
                DATA_DB_NAME,
                2
        ))

    if current_version < 3:
        # Upgrade to v3.0
        logging.info("Upgrading data database to 3.0")

        cursor.execute("""
            ALTER TABLE item ADD COLUMN deleted int DEFAULT '0'
        """)

        cursor.execute("""
            INSERT OR REPLACE INTO version (db_name, db_version)
            VALUES(?, ?)""", (
                DATA_DB_NAME,
                3
        ))

    if current_version < 4:
        # Upgrade to v4.0
        logging.info("Upgrading data database to 4.0")

        query_results = cursor.execute("""
                SELECT * FROM item_audit
            """)
        
        result = []
        for row in query_results:
            # Temporarily store in result list, can't reuse cursor
            result.append(row)

        for row in result:
            cursor.execute("""
                INSERT OR IGNORE INTO audit (date, type, id, user, event, before, after)
                VALUES(?, ?, ?, ?, ?, ?, ?)""", (
                    int(row[0]), 
                    str("ITEM"),
                    str(row[1]), 
                    str(row[2]), 
                    str(row[3]),
                    str(row[4]),
                    str(row[5])
            ))

        cursor.execute("""
            INSERT OR REPLACE INTO version (db_name, db_version)
            VALUES(?, ?)""", (
                DATA_DB_NAME,
                4
        ))

    # Finally, commit the changes and close the cursor.
    db_connection.commit()
    cursor.close()

####################
# LOG DB FUNCTIONS #
####################

def __init_log_db():
    db_connection = sqlite3.connect(LOG_DB_PATH)
    __check_log_table(db_connection)
    __upgrade_log_db(db_connection)

def __get_log_db():
    db_connection = sqlite3.connect(LOG_DB_PATH)
    db_connection.execute('pragma journal_mode=wal')
    return db_connection

def __check_log_table(db_connection):
    cursor = db_connection.cursor()
    logging.info("Checking log table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS error_log (
            date int, source text, log_level int, log_level_name text, message text, args text, 
            module text, function_name text, line_num int, exception text, process int, thread text, thread_name text
        )"""
    )

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS access_log (
            date int, source text, log_level int, log_level_name text, message text, args text, 
            module text, function_name text, line_num int, exception text, process int, thread text, thread_name text
        )"""
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
            LOG_DB_NAME,
            LOG_DB_VERSION
    ))

    db_connection.commit()
    cursor.close()

def __upgrade_log_db(db_connection):
    current_version = -1
    cursor = db_connection.cursor()

    # Get current db version
    query_results = cursor.execute("""
        SELECT db_version FROM version WHERE db_name=?""", (
            str(LOG_DB_NAME),
    ))

    for row in query_results:
        current_version = int(row[0])

    logging.info("Latest log database version: " + str(current_version))
    logging.info("Expected log database version: " + str(LOG_DB_VERSION))

    if current_version == -1:
        raise Exception("Error: was not able to pull the current log db version")
    
    if current_version == LOG_DB_VERSION:
        logging.info("No log database update is needed.")
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

# Get user if authenticated, otherwise fall back to ip address
def get_username(user):
    username = ""

    if not user:
        return "unknown"

    try:
        if user.is_authenticated:
            username = user.email
        else:
            ip_address = ""
            if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
                ip_address = str(request.environ['REMOTE_ADDR'])
            else:
                ip_address = str(request.environ['HTTP_X_FORWARDED_FOR']) # if behind a proxy
            username = ip_address
        return username
    except:
        return "unknown"