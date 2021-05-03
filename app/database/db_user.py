from . import db_util as db

###################
# USER FUNCTIONS #
###################

# Insert a new user
def insert_user(user_id, user_name, user_email, user_role, user_picture):
    db_connection = db.get_db()
    cursor = db_connection.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO user (user_id, user_name, user_email, user_role, user_picture)
        VALUES(?, ?, ?, ?, ?)""", (
            str(user_id).strip(),
            str(user_name).strip(),
            str(user_email).strip(),
            int(user_role),
            str(user_picture).strip()
        ))
    
    # Save (commit) the changes
    db_connection.commit()
    cursor.close()

# Return true if user id already exists
def exists_user_id(user_id):
    cursor = db.get_db().cursor()

    query_result = cursor.execute("""
        SELECT EXISTS(SELECT 1 FROM user WHERE user_id=? LIMIT 1)""", (
            str(user_id).strip(),
    ))
    
    for row in query_result:
        exists = (row[0] == 1)
        cursor.close()
        return exists

# Get a user for a given user_id
def get_user(user_id):
    result = None
    cursor = db.get_db().cursor()

    query_results = cursor.execute("""
        SELECT * FROM user WHERE user_id=?""", (
            str(user_id).strip(),
    ))

    for row in query_results:
        result = {
            'user_id': str(row[0]),
            'user_name': str(row[1]),
            'user_email': str(row[2]),
            'user_role': int(row[3]),
            'user_picture': str(row[4])
        }

    cursor.close()
    return result

# Get all users
def get_all_users():
    result = []
    cursor = db.get_db().cursor()

    query_results = cursor.execute("""
        SELECT * FROM user""", (
    ))

    for row in query_results:
        result.append({
            'user_id': str(row[0]),
            'user_name': str(row[1]),
            'user_email': str(row[2]),
            'user_role': int(row[3]),
            'user_picture': str(row[4])
        })

    cursor.close()
    return result

# Update the role for a given user_id
def update_user_role(user_id, new_role):
    db_connection = db.get_db()
    cursor = db_connection.cursor()

    cursor.execute("""
        UPDATE user SET user_role=? WHERE user_id=?""", (
            int(new_role),
            str(user_id).strip()
        ))
    
    # Save (commit) the changes
    db_connection.commit()
    cursor.close()

# Update the user information
def update_user_info(user_id, user_name, user_email, user_picture):
    db_connection = db.get_db()
    cursor = db_connection.cursor()

    cursor.execute("""
        UPDATE user SET user_name=?, user_email=?, user_picture=? WHERE user_id=?""", (
            str(user_name).strip(),
            str(user_email).strip(),
            str(user_picture).strip(),
            str(user_id).strip()
        ))
    
    # Save (commit) the changes
    db_connection.commit()
    cursor.close()

# Delete a user for a given user_id
def delete_user(user_id):
    db_connection = db.get_db()
    cursor = db_connection.cursor()

    query_results = cursor.execute("""
        DELETE FROM user WHERE user_id=?""", (
            str(user_id).strip(),
    ))

    db_connection.commit()
    cursor.close()
