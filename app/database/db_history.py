from datetime import datetime
from flask import request

from . import db_util as db

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
    db_connection = db.get_db()
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