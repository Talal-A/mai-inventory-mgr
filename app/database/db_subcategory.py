from . import db_util as db
from . import db_audit, db_category
import uuid

######################
# SUBCATEGORY FUNCTIONS #
######################

# Insert a new category
def insert_subcategory(subcategory_name, category_id):
    subcategory_id = str(uuid.uuid4())

    db_connection = db.get_data_db()
    cursor = db_connection.cursor()
    x = cursor.execute("""
        INSERT OR IGNORE INTO subcategory (subcategory_id, category_id, name, deleted)
        VALUES(?, ?, ?, ?)""", (
            str(subcategory_id).strip(),
            str(category_id).strip(),
            str(subcategory_name).strip(),
            0,
        ))
    db_connection.commit()
    cursor.close()

    # Log the creation of the new category
    db_audit.insert_subcategory_audit_event(category_id, "Created subcategory.", "", get_subcategory(subcategory_id))

# Return true if a subcategory with the same name already exists within the parent category
def exists_subcategory_name(subcategory_name, category_id):
    cursor = db.get_data_db().cursor()
    print(subcategory_name)
    print(category_id)
    query_result = cursor.execute("""
        SELECT EXISTS(SELECT 1 FROM subcategory WHERE name=? and category_id=? LIMIT 1)""", (
            str(subcategory_name).strip(),
            str(category_id).strip(),
    ))
    
    for row in query_result:
        exists = (row[0] == 1)
        cursor.close()
        return exists

# Return true if the subcategory id already exists
def exists_subcategory_id(subcategory_id):
    cursor = db.get_data_db().cursor()

    query_result = cursor.execute("""
        SELECT EXISTS(SELECT 1 FROM subcategory WHERE subcategory_id=? LIMIT 1)""", (
            str(subcategory_id).strip(),
    ))
    
    for row in query_result:
        exists = (row[0] == 1)
        cursor.close()
        return exists

# Return true if subcategory is actively used by an item
def exists_subcategory_usage(subcategory_id):
    cursor = db.get_data_db().cursor()

    query_result = cursor.execute("""
        SELECT EXISTS(SELECT 1 FROM item WHERE subcategory_id=? and deleted=0 LIMIT 1)""", (
            str(subcategory_id).strip(),
    ))
    
    for row in query_result:
        exists = (row[0] == 1)
        cursor.close()
        return exists

# Get a category for a given subcategory_id
def get_subcategory(subcategory_id):
    result = None
    cursor = db.get_data_db().cursor()

    query_results = cursor.execute("""
        SELECT * FROM subcategory WHERE subcategory_id=?""", (
            str(subcategory_id).strip(),
    ))

    for row in query_results:
        result = {
            'id': str(row[0]),
            'category_id': str(row[1]),
            'name': str(row[2]),
            'deleted': int(row[3])
        }

    cursor.close()
    return result

# Get all subcategories
def get_all_subcategories():
    result = []
    cursor = db.get_data_db().cursor()

    query_results = cursor.execute("""
        SELECT * FROM subcategory ORDER BY name COLLATE NOCASE ASC""", (
    ))

    for row in query_results:
        result.append({
            'id': str(row[0]),
            'category_id': str(row[1]),
            'category_name': db_category.get_category(str(row[1]))['name'],
            'name': str(row[2]),
        })

    cursor.close()
    return result

# Get all subcategories within a given category
def get_all_subcategories_for_category(category_id):
    result = []
    cursor = db.get_data_db().cursor()

    query_results = cursor.execute("""
        SELECT * FROM subcategory WHERE category_id=? ORDER BY name COLLATE NOCASE ASC""", (
            str(category_id).strip(),
    ))

    for row in query_results:
        result.append({
            'id': str(row[0]),
            'category_id': str(row[1]),
            'category_name': db_category.get_category(str(row[1]))['name'],
            'name': str(row[2]),
        })

    cursor.close()
    return result

# Get all active subcategories 
def get_all_active_subcategories():
    result = []
    cursor = db.get_data_db().cursor()

    query_results = cursor.execute("""
        SELECT * FROM subcategory WHERE deleted=0 ORDER BY name COLLATE NOCASE ASC""", (
    ))

    for row in query_results:
        result.append({
            'id': str(row[0]),
            'category_id': str(row[1]),
            'category_name': db_category.get_category(str(row[1]))['name'],
            'name': str(row[2]),
        })

    cursor.close()
    return result

# Get all active subcategories within a given category
def get_all_active_subcategories_for_category(category_id):
    result = []
    cursor = db.get_data_db().cursor()

    query_results = cursor.execute("""
        SELECT * FROM subcategory WHERE deleted=0 and category_id=? ORDER BY name COLLATE NOCASE ASC""", (
            str(category_id).strip(),
    ))

    for row in query_results:
        result.append({
            'id': str(row[0]),
            'name': str(row[2])
        })

    cursor.close()
    return result


# Get all deleted subcategories within a given category
def get_all_deleted_subcategories(category_id):
    result = []
    cursor = db.get_data_db().cursor()

    query_results = cursor.execute("""
        SELECT * FROM subcategory WHERE deleted=1 and category_id=? ORDER BY name COLLATE NOCASE ASC""", (
            str(category_id).strip(),
    ))

    for row in query_results:
        result.append({
            'id': str(row[0]),
            'name': str(row[2])
        })

    cursor.close()
    return result

# Get all subcategories which can be deleted safely (not referenced by any items)
def get_deletable_subcategories():
    all_subcategories = get_all_active_subcategories()
    deletable_subcategories = []
    for subcategory in all_subcategories:
        if not exists_subcategory_usage(subcategory['id']):
            deletable_subcategories.append(subcategory)
    return deletable_subcategories

# Update the name for a given subcategory_id
def update_subcategory_name(subcategory_id, new_name):
    db_connection = db.get_data_db()
    cursor = db_connection.cursor()
    subcategory_before = get_subcategory(subcategory_id)

    cursor.execute("""
        UPDATE subcategory SET name=? WHERE subcategory_id=?""", (
            str(new_name).strip(),
            str(subcategory_id).strip()
        ))
    
    # Save (commit) the changes
    db_connection.commit()
    cursor.close()

    db_audit.insert_subcategory_audit_event(subcategory_id, "Edited subcategory.", subcategory_before, get_subcategory(subcategory_id))

# Delete a subcategory for a given subcategory_id
def delete_subcategory(subcategory_id):
    if exists_subcategory_usage(subcategory_id):
        # Cannot delete an actively used subcategory
        return 
    
    db_connection = db.get_data_db()
    cursor = db_connection.cursor()
    subcategory_before = get_subcategory(subcategory_id)

    query_results = cursor.execute("""
        UPDATE subcategory SET deleted=? WHERE subcategory_id=?""", (
            1,
            str(subcategory_id).strip(),
    ))

    db_connection.commit()
    cursor.close()

    db_audit.insert_subcategory_audit_event(subcategory_id, "Deleted subcategory.", subcategory_before, get_subcategory(subcategory_id))

# Restore a subcategory for a given subcategory_id
def restore_subcategory(subcategory_id):    
    db_connection = db.get_data_db()
    cursor = db_connection.cursor()
    subcategory_before = get_subcategory(subcategory_id)

    query_results = cursor.execute("""
        UPDATE subcategory SET deleted=? WHERE subcategory_id=?""", (
            0,
            str(subcategory_id).strip(),
    ))

    db_connection.commit()
    cursor.close()

    db_audit.insert_subcategory_audit_event(subcategory_id, "Restored subcategory.", subcategory_before, get_subcategory(subcategory_id))