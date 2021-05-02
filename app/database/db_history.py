from datetime import datetime

from . import db_util as db

#####################
# HISTORY FUNCTIONS #
#####################

# Insert a new history event
# TODO: can we just import current_user and use it directly here, instead of passing it in as a parameter?
def insert_history(type, user, event):
    db_connection = db.get_db()
    cursor = db_connection.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO history (date, type, user, event)
        VALUES(?, ?, ?, ?)""", (
            datetime.now().timestamp(), 
            str(type), 
            str(db.get_username(user)), 
            str(event)
        ))
    
    # Save (commit) the changes
    db_connection.commit()
    cursor.close()

# Get all history events
def get_history():
    result = []
    cursor = db.get_db().cursor()

    query_results = cursor.execute("""
        SELECT * FROM history ORDER BY date DESC"""
    )

    for row in query_results:
        result.append({
            'date_raw': int(row[0]),
            'date': db.format_timestamp(int(row[0])),
            'type': str(row[1]),
            'user': str(row[2]),
            'event': str(row[3])
        })
    cursor.close()
    return result