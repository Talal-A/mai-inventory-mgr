import pymongo
from bson.objectid import ObjectId

myclient = pymongo.MongoClient("mongodb://nerv:9201/")
mydb = myclient["MAI_UCLA_DB"]

CATEGORY_DB = mydb["category"]
ITEM_DB = mydb["item"]

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

def insertItem(category_id, name, location="", quantity_active=0, quantity_expired=0, notes="", barcodes=[]):
    if str(name).strip() not in getItemNames(): ITEM_DB.insert_one({
            "category_id": str(category_id).strip(),
            "name": str(name).strip(),
            "location": location,
            "quantity_active": 0,
            "quantity_expired": 0,
            "notes": notes,
            "barcodes": barcodes})

