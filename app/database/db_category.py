from . import db_util as db
import uuid

######################
# CATEGORY FUNCTIONS #
######################

# Insert a new category
def insert_category(category_name):
    category_id = str(uuid.uuid4())

    db_connection = db.get_data_db()
    cursor = db_connection.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO category (category_id, name)
        VALUES(?, ?)""", (
            str(category_id).strip(),
            str(category_name).strip()
        ))

    db_connection.commit()
    cursor.close()

# Return true if a category with the same name already exists
def exists_category_name(category_name):
    cursor = db.get_data_db().cursor()

    query_result = cursor.execute("""
        SELECT EXISTS(SELECT 1 FROM category WHERE name=? LIMIT 1)""", (
            str(category_name).strip(),
    ))
    
    for row in query_result:
        exists = (row[0] == 1)
        cursor.close()
        return exists

# Return true if the category id already exists
def exists_category_id(category_id):
    cursor = db.get_data_db().cursor()

    query_result = cursor.execute("""
        SELECT EXISTS(SELECT 1 FROM category WHERE category_id=? LIMIT 1)""", (
            str(category_id).strip(),
    ))
    
    for row in query_result:
        exists = (row[0] == 1)
        cursor.close()
        return exists

# Return true if category is actively used by an item
def exists_category_usage(category_id):
    cursor = db.get_data_db().cursor()

    query_result = cursor.execute("""
        SELECT EXISTS(SELECT 1 FROM item WHERE category_id=? LIMIT 1)""", (
            str(category_id).strip(),
    ))
    
    for row in query_result:
        exists = (row[0] == 1)
        cursor.close()
        return exists

# Get a category for a given category_id
def get_category(category_id):
    result = None
    cursor = db.get_data_db().cursor()

    query_results = cursor.execute("""
        SELECT * FROM category WHERE category_id=?""", (
            str(category_id).strip(),
    ))

    for row in query_results:
        result = {
            'id': str(row[0]),
            'name': str(row[1])
        }

    cursor.close()
    return result

# Get all categories
def get_all_categories():
    result = []
    cursor = db.get_data_db().cursor()

    query_results = cursor.execute("""
        SELECT * FROM category""", (
    ))

    for row in query_results:
        result.append({
            'id': str(row[0]),
            'name': str(row[1])
        })

    cursor.close()
    return result

# Get all categories which can be deleted safely (not referenced by any items)
def get_deletable_categories():
    all_categories = get_all_categories()
    deletable_categories = []
    for category in all_categories:
        if not exists_category_usage(category['id']):
            deletable_categories.append(category)
    return deletable_categories

# Update the name for a given category_id
def update_category_name(category_id, new_name):
    db_connection = db.get_data_db()
    cursor = db_connection.cursor()

    cursor.execute("""
        UPDATE category SET name=? WHERE category_id=?""", (
            str(new_name).strip(),
            str(category_id).strip()
        ))
    
    # Save (commit) the changes
    db_connection.commit()
    cursor.close()

# Delete a category for a given category_id
def delete_category(category_id):
    if exists_category_usage(category_id):
        # Cannot delete an actively used category
        return 
    
    db_connection = db.get_data_db()
    cursor = db_connection.cursor()

    query_results = cursor.execute("""
        DELETE FROM category WHERE category_id=?""", (
            str(category_id).strip(),
    ))

    db_connection.commit()
    cursor.close()