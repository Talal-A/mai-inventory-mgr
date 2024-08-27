from . import db_util as db
from . import db_audit, db_subcategory
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
        INSERT OR IGNORE INTO category (category_id, name, deleted)
        VALUES(?, ?, ?)""", (
            str(category_id).strip(),
            str(category_name).strip(),
            0
        ))

    db_connection.commit()
    cursor.close()

    # Log the creation of the new category
    db_audit.insert_category_audit_event(category_id, "Created category.", "", get_category(category_id))
    db_subcategory.insert_subcategory('General', category_id)

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
        SELECT EXISTS(SELECT 1 FROM item WHERE category_id=? and deleted=0 LIMIT 1)""", (
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
            'name': str(row[1]),
            'deleted': int(row[2])
        }

    cursor.close()
    return result

# Get all categories
def get_all_categories():
    result = []
    cursor = db.get_data_db().cursor()

    query_results = cursor.execute("""
        SELECT * FROM category ORDER BY name COLLATE NOCASE ASC""", (
    ))

    for row in query_results:
        result.append({
            'id': str(row[0]),
            'name': str(row[1])
        })

    cursor.close()
    return result

# Get all active categories
def get_all_active_categories():
    result = []
    cursor = db.get_data_db().cursor()

    query_results = cursor.execute("""
        SELECT * FROM category WHERE deleted=0 ORDER BY name COLLATE NOCASE ASC""", (
    ))

    for row in query_results:
        result.append({
            'id': str(row[0]),
            'name': str(row[1])
        })

    cursor.close()
    return result


# Get all deleted categories
def get_all_deleted_categories():
    result = []
    cursor = db.get_data_db().cursor()

    query_results = cursor.execute("""
        SELECT * FROM category WHERE deleted=1 ORDER BY name COLLATE NOCASE ASC""", (
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
    all_categories = get_all_active_categories()
    deletable_categories = []
    for category in all_categories:
        if not exists_category_usage(category['id']):
            deletable_categories.append(category)
    return deletable_categories

# Update the name for a given category_id
def update_category_name(category_id, new_name):
    db_connection = db.get_data_db()
    cursor = db_connection.cursor()
    category_before = get_category(category_id)

    cursor.execute("""
        UPDATE category SET name=? WHERE category_id=?""", (
            str(new_name).strip(),
            str(category_id).strip()
        ))
    
    # Save (commit) the changes
    db_connection.commit()
    cursor.close()

    db_audit.insert_category_audit_event(category_id, "Edited category.", category_before, get_category(category_id))

# Delete a category for a given category_id
def delete_category(category_id):
    if exists_category_usage(category_id):
        # Cannot delete an actively used category
        return 
    
    db_connection = db.get_data_db()
    cursor = db_connection.cursor()
    category_before = get_category(category_id)

    query_results = cursor.execute("""
        UPDATE category SET deleted=? WHERE category_id=?""", (
            1,
            str(category_id).strip(),
    ))

    db_connection.commit()
    cursor.close()

    db_audit.insert_category_audit_event(category_id, "Deleted category.", category_before, get_category(category_id))

# Restore a category for a given category_id
def restore_category(category_id):    
    db_connection = db.get_data_db()
    cursor = db_connection.cursor()
    category_before = get_category(category_id)

    query_results = cursor.execute("""
        UPDATE category SET deleted=? WHERE category_id=?""", (
            0,
            str(category_id).strip(),
    ))

    db_connection.commit()
    cursor.close()

    db_audit.insert_category_audit_event(category_id, "Restored category.", category_before, get_category(category_id))