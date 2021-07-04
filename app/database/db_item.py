import uuid

from . import db_util as db
from . import db_barcode, db_category, db_image, db_audit

##################
# ITEM FUNCTIONS #
##################

# Insert an item
def insert_item(category_id, name, location="", quantity_active=0, quantity_expired=0, notes="", url=""):
    item_id = str(uuid.uuid4())

    db_connection = db.get_data_db()
    cursor = db_connection.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO item (item_id, category_id, name, location, quantity_active, quantity_expired, notes, url, deleted)
        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)""", (
            str(item_id).strip(),
            str(category_id).strip(),
            str(name).strip(),
            str(location).strip(),
            int(quantity_active),
            int(quantity_expired),
            str(notes),
            str(url).strip(),
            0
        ))

    db_connection.commit()
    cursor.close()

    # Log the creation of the new item.
    db_audit.insert_item_audit_event(item_id, "Created item.", "", get_item(item_id))

    return item_id

# Return true if item_id already exists
def exists_item_id(item_id):
    cursor = db.get_data_db().cursor()

    query_result = cursor.execute("""
        SELECT EXISTS(SELECT 1 FROM item WHERE item_id=? LIMIT 1)""", (
            str(item_id).strip(),
    ))
    
    for row in query_result:
        exists = (row[0] == 1)
        cursor.close()
        return exists

# Get an item for a given item_id
def get_item(item_id):
    result = None
    cursor = db.get_data_db().cursor()

    query_results = cursor.execute("""
        SELECT * FROM item WHERE item_id=?""", (
            str(item_id).strip(),
    ))

    for row in query_results:
        result = {
            'id': str(row[0]),
            'category_id': str(row[1]),
            'category_name': db_category.get_category(str(row[1]))['name'],
            'name': str(row[2]),
            'location': str(row[3]),
            'quantity_active': int(row[4]),
            'quantity_expired': int(row[5]),
            'notes': str(row[6]),
            'url': str(row[7]),
            'deleted': bool(row[8])
        }

    cursor.close()
    return result

# Get all items
def get_all_items():
    result = []
    cursor = db.get_data_db().cursor()
    
    # # Cache list of categories
    cached_categories = {}
    for category in db_category.get_all_categories():
        cached_categories[category['id']] = category['name']

    query_results = cursor.execute("""
        SELECT * FROM item WHERE deleted=0 ORDER BY name COLLATE NOCASE ASC""", (
    ))

    for row in query_results:
        result.append({
            'id': str(row[0]),
            'category_id': str(row[1]),
            'category_name': cached_categories[str(row[1])],
            'name': str(row[2]),
            'location': str(row[3]),
            'quantity_active': int(row[4]),
            'quantity_expired': int(row[5]),
            'notes': str(row[6]),
            'url': str(row[7]),
            'deleted': bool(row[8])
        })

    cursor.close()
    result.sort(key=lambda k: str(k['category_name']).lower())
    return result

# Get all deleted items
def get_all_deleted_items():
    result = []
    cursor = db.get_data_db().cursor()
    
    # # Cache list of categories
    cached_categories = {}
    for category in db_category.get_all_categories():
        cached_categories[category['id']] = category['name']

    query_results = cursor.execute("""
        SELECT * FROM item WHERE deleted=1 ORDER BY name COLLATE NOCASE ASC""", (
    ))

    for row in query_results:
        result.append({
            'id': str(row[0]),
            'category_id': str(row[1]),
            'category_name': cached_categories[str(row[1])],
            'name': str(row[2]),
            'location': str(row[3]),
            'quantity_active': int(row[4]),
            'quantity_expired': int(row[5]),
            'notes': str(row[6]),
            'url': str(row[7]),
            'deleted': bool(row[8])
        })

    cursor.close()
    result.sort(key=lambda k: str(k['category_name']).lower())
    return result

# Get all items under a given category
def get_all_items_for_category(category_id):
    result = []
    cursor = db.get_data_db().cursor()

    # Cache category name
    cached_category_name = db_category.get_category(str(category_id).strip())['name']

    query_results = cursor.execute("""
        SELECT * FROM item WHERE category_id=? and deleted=0 ORDER BY name COLLATE NOCASE ASC""", (
            str(category_id).strip(),
    ))

    for row in query_results:
        result.append({
            'id': str(row[0]),
            'category_id': str(row[1]),
            'category_name': cached_category_name,
            'name': str(row[2]),
            'location': str(row[3]),
            'quantity_active': int(row[4]),
            'quantity_expired': int(row[5]),
            'notes': str(row[6]),
            'url': str(row[7]),
            'deleted': bool(row[8])
        })

    cursor.close()
    return result

# Update an item with new values
def update_item(item_id, category_id, location, quantity_active, quantity_expired, notes, url):
    db_connection = db.get_data_db()
    cursor = db_connection.cursor()
    item_before = get_item(item_id)

    cursor.execute("""
        UPDATE item SET category_id=?, location=?, quantity_active=?, quantity_expired=?, notes=?, url=? WHERE item_id=?""", (
            str(category_id).strip(),
            str(location).strip(),
            int(quantity_active),
            int(quantity_expired),
            str(notes),
            str(url).strip(),
            str(item_id).strip()
        ))
    
    # Save (commit) the changes
    db_connection.commit()
    cursor.close()

    db_audit.insert_item_audit_event(item_id, "Edited item.", item_before, get_item(item_id))

# Update an item's active quantity
def update_item_quantity(item_id, new_active_quantity):
    db_connection = db.get_data_db()
    cursor = db_connection.cursor()
    item_before = get_item(item_id)

    cursor.execute("""
        UPDATE item SET quantity_active=? WHERE item_id=?""", (
            int(new_active_quantity),
            str(item_id).strip()
        ))
    
    # Save (commit) the changes
    db_connection.commit()
    cursor.close()

    db_audit.insert_item_audit_event(item_id, "Updated quantity.", item_before, get_item(item_id))

# Delete an item for a given item_id
def delete_item(item_id):
    db_connection = db.get_data_db()
    cursor = db_connection.cursor()
    item_before = get_item(item_id)

    query_results = cursor.execute("""
        UPDATE item SET deleted=? WHERE item_id=?""", (
            1,
            str(item_id).strip(),
    ))

    db_connection.commit()
    cursor.close()

    db_audit.insert_item_audit_event(item_id, "Deleted item.", item_before, get_item(item_id))

    db_barcode.delete_barcodes_for_item(item_id)

# Undo deletion of an item for a given item_id
def restore_deleted_item(item_id):
    db_connection = db.get_data_db()
    cursor = db_connection.cursor()
    item_before = get_item(item_id)

    query_results = cursor.execute("""
        UPDATE item SET deleted=? WHERE item_id=?""", (
            0,
            str(item_id).strip(),
    ))

    db_connection.commit()
    cursor.close()

    db_audit.insert_item_audit_event(item_id, "Restored item.", item_before, get_item(item_id))