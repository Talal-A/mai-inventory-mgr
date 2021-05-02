from . import db_util as db
from flask_login import current_user
from datetime import datetime

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
            str(before),
            str(after)
        ))

    # Save (commit) the changes
    db_connection.commit()
    cursor.close()

