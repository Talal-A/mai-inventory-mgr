from . import db_util as db
from . import db_item, db_item_audit

#####################
# BARCODE FUNCTIONS #
#####################

# Insert a new barcode
def insert_barcode(barcode, item_id):
    db_connection = db.get_data_db()
    cursor = db_connection.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO barcode (barcode, item_id)
        VALUES(?, ?)""", (
            str(barcode).strip(),
            str(item_id)
        ))
    
    # Save (commit) the changes
    db_connection.commit()
    cursor.close()

    db_item_audit.insert_item_audit_event(item_id, "Added barcode.", "", get_barcode(barcode))

# Return true if barcode already exists
def exists_barcode(barcode):
    cursor = db.get_data_db().cursor()

    query_result = cursor.execute("""
        SELECT EXISTS(SELECT 1 FROM barcode WHERE barcode=? LIMIT 1)""", (
            str(barcode).strip(),
    ))
    
    for row in query_result:
        exists = (row[0] == 1)
        cursor.close()
        return exists

# Get item_id associated with a given barcode
def get_barcode(barcode):
    result = None
    cursor = db.get_data_db().cursor()

    query_results = cursor.execute("""
        SELECT * FROM barcode WHERE barcode=?""", (
            str(barcode).strip(),
    ))

    for row in query_results:
        result = {
            'barcode': str(row[0]),
            'item_id': str(row[1])
        }

    cursor.close()
    return result

# Return all barcodes associated with an item_id
def get_barcodes_for_item(item_id):
    result = []
    cursor = db.get_data_db().cursor()

    query_results = cursor.execute("""
        SELECT * FROM barcode WHERE item_id=? """, (
            str(item_id),
    ))

    for row in query_results:
        result.append({
            'barcode': str(row[0]),
            'item_id': str(row[1])
        })

    cursor.close()
    return result

# Return all barcodes
def get_all_barcodes():
    result = []
    cursor = db.get_data_db().cursor()

    query_results = cursor.execute("""
        SELECT * FROM barcode"""
    )

    for row in query_results:
        result.append({
            'barcode': str(row[0]),
            'item_id': str(row[1]),
            'item_name': db_item.get_item(str(row[1]))['name']
        })

    cursor.close()
    return result

# Delete a single barcode
def delete_barcode(barcode):
    db_connection = db.get_data_db()
    cursor = db_connection.cursor()
    barcode_before = get_barcode(barcode)

    query_results = cursor.execute("""
        DELETE FROM barcode WHERE barcode=?""", (
            str(barcode).strip(),
    ))

    db_connection.commit()
    cursor.close()

    db_item_audit.insert_item_audit_event(barcode_before['item_id'], "Deleted barcode.", barcode_before, "")

# Delete all barcodes associated with an item_id
def delete_barcodes_for_item(item_id):
    db_connection = db.get_data_db()
    cursor = db_connection.cursor()
    barcodes_before = get_barcodes_for_item(item_id)

    query_results = cursor.execute("""
        DELETE FROM barcode WHERE item_id=?""", (
            str(item_id),
    ))

    db_connection.commit()
    cursor.close()

    db_item_audit.insert_item_audit_event(item_id, "Deleted all barcodes.", barcodes_before, "")