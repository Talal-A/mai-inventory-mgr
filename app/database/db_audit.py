from . import db_util as db
from flask_login import current_user
from datetime import datetime
import json

ITEM_TYPE = 'ITEM'
CATEGORY_TYPE = 'CATEGORY'
USER_TYPE = 'USER'

# Insert a new item audit event
def insert_item_audit_event(item_id, event, before, after):
    __insert_audit_event(ITEM_TYPE, item_id, event, before, after)

# Insert a new category audit event
def insert_category_audit_event(category_id, event, before, after):
    __insert_audit_event(CATEGORY_TYPE, category_id, event, before, after)

# Insert a new user audit event
def insert_user_audit_event(user_id, event, before, after):
    __insert_audit_event(USER_TYPE, user_id, event, before, after)

def __insert_audit_event(type, id, event, before, after):
    if before == after:
        return

    db_connection = db.get_data_db()
    cursor = db_connection.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO audit (date, type, id, user, event, before, after)
        VALUES(?, ?, ?, ?, ?, ?, ?)""", (
            datetime.now().timestamp(), 
            str(type),
            str(id), 
            str(db.get_username(current_user)), 
            str(event),
            json.dumps(before),
            json.dumps(after)
        ))

    # Save (commit) the changes
    db_connection.commit()
    cursor.close()

def get_item_audit(item_id):
    result = []
    cursor = db.get_data_db().cursor()

    query_results = cursor.execute("""
        SELECT * FROM audit WHERE type=? and id=? ORDER BY date DESC""", (
            str(ITEM_TYPE).strip(),
            str(item_id).strip(),    
    ))

    for row in query_results:
        result.append({
            'date_raw': int(row[0]),
            'date': db.format_timestamp(int(row[0])),
            'type': str(row[1]),
            'item_id': str(row[2]),
            'user': str(row[3]),
            'event': str(row[4]),
            'before': str(row[5]),
            'after': str(row[6])
        })

    cursor.close()
    return result

def get_all_audit():
    result = []

    cursor = db.get_data_db().cursor()

    query_results = cursor.execute("""
        SELECT * FROM audit ORDER BY date DESC
    """)

    for row in query_results:
        result.append({
            'date_raw': int(row[0]),
            'date': db.format_timestamp(int(row[0])),
            'type': str(row[1]),
            'id': str(row[2]),
            'user': str(row[3]),
            'event': str(row[4]),
            'before': str(row[5]),
            'after': str(row[6])
        })

    cursor.close()
    return result