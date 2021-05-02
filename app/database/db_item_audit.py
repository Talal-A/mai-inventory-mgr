from . import db_util as db
from flask_login import current_user
from datetime import datetime
import json

# Insert a new item audit event
def insert_item_audit_event(item_id, event, before, after):
    db_connection = db.get_db()
    cursor = db_connection.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO item_audit (date, item_id, user, event, before, after)
        VALUES(?, ?, ?, ?, ?, ?)""", (
            datetime.now().timestamp(), 
            str(item_id), 
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
    cursor = db.get_db().cursor()

    query_results = cursor.execute("""
        SELECT * FROM item_audit WHERE item_id=? ORDER BY date DESC""", (
            str(item_id).strip(),    
    ))

    for row in query_results:
        result.append({
            'date_raw': int(row[0]),
            'date': db.format_timestamp(int(row[0])),
            'item_id': str(row[1]),
            'user': str(row[2]),
            'event': str(row[3]),
            'before': str(row[4]),
            'after': str(row[5])
        })

    cursor.close()
    return result