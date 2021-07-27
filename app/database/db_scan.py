from . import db_item, db_barcode

##################
# SCAN FUNCTIONS #
##################

# Safely update quantity for an item, using a barcode
def scan_barcode_update_quantity(barcode_id, diff, type):
    barcode = db_barcode.get_barcode(barcode_id)
    if barcode == None:
        return False
    item = db_item.get_item(barcode['item_id'])
    if item == None:
        return False
    else:
        new_quantity = item[str(type).strip()]
        new_quantity += diff
        if new_quantity < 0:
            return False
        else:
            # Perform update and return true
            db_item.update_item_quantity(item['id'], new_quantity, str(type).strip())
            return True

# Safely update quantity for an item
def search_item_update_quantity(item_id, diff, type):
    item = db_item.get_item(item_id)
    if item == None:
        return False
    else:
        new_quantity = item[str(type).strip()]
        new_quantity += diff
        if new_quantity < 0:
            return False
        else:
            # Perform update and return true
            db_item.update_item_quantity(item['id'], new_quantity, str(type).strip())
            return True