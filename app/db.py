import pymongo
from bson.objectid import ObjectId

myclient = pymongo.MongoClient("mongodb://nerv:9201/")
mydb = myclient["MAI_UCLA_DB"]

CATEGORY_DB = mydb["category"]
ITEM_DB = mydb["item"]
BARCODE_DB = mydb["barcode"]

def getDeletableCategories():
    items = getItems()
    result = []
    for category in getCategories():
        if not categoryInUse(category['id'], items):
            result.append(category)
    return result

def categoryInUse(category_id, items):
    for item in items:
        if str(category_id) == str(item['category_id']):
            return True
    return False

def deleteCategory(category_id):
    query = {'_id': ObjectId(category_id)}
    CATEGORY_DB.delete_one(query)

def getCategoryNames():
    result = []
    for item in CATEGORY_DB.find():
        result.append(item['name'])
    return result

def getCategories():
    result = []
    for item in CATEGORY_DB.find():
        result.append({'id': item['_id'], 'name': item['name']})
    return result

def getCategoryForId(uuid):
    category = {}
    for item in getCategories():
        if str(item['id']) == str(uuid):
            category = item
    return category

def updateCategory(uuid, newName):
    CATEGORY_DB.update_one({'_id': ObjectId(uuid)}, {"$set": {"name": str(newName).strip()}})

def insertCategory(newCategory):
    if str(newCategory) not in getCategoryNames():
        CATEGORY_DB.insert_one({"name": str(newCategory).strip()})

def getItemForId(uuid):
    result = {}
    for item in getItems():
        if str(item['id']) == str(uuid):
            result = item
    return result

def getItems():
    result = []
    for item in ITEM_DB.find():
        result.append({
            'id': item['_id'],
            'category_id': item['category_id'],
            'category_name': getCategoryForId(item['category_id'])['name'],
            'name': item['name'], 
            'location': item['location'], 
            'quantity_active': item['quantity_active'], 
            'quantity_expired': item['quantity_expired'], 
            'notes': item['notes'], 
            'barcodes': item['barcodes']})
    return result

def getItemNames():
    result = []
    for item in ITEM_DB.find():
        result.append(item['name'])
    return result

def updateItem(uuid, category_id, location, quantity_active, quantity_expired, notes):
    ITEM_DB.update_one({'_id': ObjectId(uuid)}, {"$set": {
        "category_id": str(category_id).strip(),
        "location": str(location).strip(),
        "quantity_active": int(quantity_active),
        "quantity_expired": int(quantity_expired),
        "notes": str(notes)
        }})

def insertItem(category_id, name, location="", quantity_active=0, quantity_expired=0, notes="", barcodes=[]):
    if str(name).strip() not in getItemNames(): ITEM_DB.insert_one({
            "category_id": str(category_id).strip(),
            "name": str(name).strip(),
            "location": location,
            "quantity_active": 0,
            "quantity_expired": 0,
            "notes": notes,
            "barcodes": barcodes})

def getBarcodesForItem(item_id):
    result = []
    for barcode in BARCODE_DB.find():
        if item_id == barcode['item_id']:
            result.append(barcode)
    return result

def getBarcodes():
    result = []
    for item in BARCODE_DB.find():
        result.append(item['barcode'])
    return result

def insertBarcode(newBarcode, itemId):
    if str(newBarcode).strip() not in getBarcodes():
        BARCODE_DB.insert_one({
            "barcode": str(newBarcode).strip(),
            "item_id": str(itemId).strip()
        })

