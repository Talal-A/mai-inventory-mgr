import pymongo
from bson.objectid import ObjectId
from datetime import datetime
import pytz
from flask import request

myclient = pymongo.MongoClient("mongodb://nerv:9201/")
mydb = myclient["MAI_UCLA_DB"]

CATEGORY_DB = mydb["category"]
ITEM_DB = mydb["item"]
BARCODE_DB = mydb["barcode"]
USER_DB = mydb["user"]
HISTORY_DB = mydb["history"]

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

def getItemsForCategory(category_id):
    result = []
    for item in getItems():
        if str(category_id) == str(item['category_id']):
            result.append(item)
    return result

def getCategoryIdToNameMapping():
    result = {}
    for category in getCategories():
        result[str(category['id'])] = category['name']
    return result

def getItems(): # TODO: Add url field
    result = []
    categoryNameMap = getCategoryIdToNameMapping()
    for item in ITEM_DB.find():
        result.append({
            'id': item['_id'],
            'category_id': item['category_id'],
            'category_name': categoryNameMap[item['category_id']],
            'name': item['name'], 
            'location': item['location'], 
            'quantity_active': item['quantity_active'], 
            'quantity_expired': item['quantity_expired'], 
            'notes': item['notes'], 
            'url': item['url']})
    return result

def getItemNames():
    result = []
    for item in ITEM_DB.find():
        result.append(item['name'])
    return result

def deleteItem(item_id):
    # First delete the barcodes, if any
    for barcode in getBarcodesForItem(item_id):
        print(barcode)
        deleteBarcode(str(barcode['_id']))

    # Delete item
    query = {'_id': ObjectId(item_id)}
    ITEM_DB.delete_one(query)

def updateItem(uuid, category_id, location, quantity_active, quantity_expired, notes, url):
    ITEM_DB.update_one({'_id': ObjectId(uuid)}, {"$set": {
        "category_id": str(category_id).strip(),
        "location": str(location).strip(),
        "quantity_active": int(quantity_active),
        "quantity_expired": int(quantity_expired),
        "notes": str(notes),
        "url": str(url).strip()
        }})

def insertItem(category_id, name, location="", quantity_active=0, quantity_expired=0, notes="", url=""):
    if str(name).strip() not in getItemNames(): ITEM_DB.insert_one({
            "category_id": str(category_id).strip(),
            "name": str(name).strip(),
            "location": location,
            "quantity_active": 0,
            "quantity_expired": 0,
            "notes": notes,
            "url": url})

def getBarcodesForItem(item_id):
    result = []
    for barcode in BARCODE_DB.find():
        if item_id == barcode['item_id']:
            result.append(barcode)
    return result

def barcodeItemNameLookup(item_id, items):
    for item in items:
        if str(item_id) == str(item['id']):
            return item['name']
    return ""

def getBarcodes():
    result = []
    items = getItems()
    for barcode in BARCODE_DB.find():
        result.append({
            "id": str(barcode["_id"]),
            "barcode": barcode['barcode'],
            "item_id": barcode['item_id'],
            "item_name": barcodeItemNameLookup(barcode['item_id'], items)
        })
    return result

def getBarcodeNames():
    result = []
    for item in BARCODE_DB.find():
        result.append(item['barcode'])
    return result

def insertBarcode(newBarcode, itemId):
    if str(newBarcode).strip() not in getBarcodeNames():
        BARCODE_DB.insert_one({
            "barcode": str(newBarcode).strip(),
            "item_id": str(itemId).strip()
        })

def deleteBarcode(barcode_id):
    query = {'_id': ObjectId(barcode_id)}
    BARCODE_DB.delete_one(query)

def getBarcode(barcode_id):
    query = {'barcode': str(barcode_id)}
    return BARCODE_DB.find_one(query)

def scanBarcodeAndUpdateQuantity(barcode_id, amount):
    barcode = BARCODE_DB.find_one({'barcode': str(barcode_id)})
    item = ITEM_DB.find_one({'_id': ObjectId(barcode['item_id'])})
    if item == None:
        return False
    else:
        currentQuantity = item['quantity_active']
        currentQuantity += amount
        if currentQuantity < 0:
            return False
        else:
            # Perform update and return true
            ITEM_DB.update_one({'_id': item['_id']}, {"$set": {"quantity_active": int(currentQuantity)}})
            return True

def searchAndUpdateQuantity(item_id, amount):
    item = ITEM_DB.find_one({'_id': ObjectId(item_id)})
    if item == None:
        return False
    else:
        currentQuantity = item['quantity_active']
        currentQuantity += amount
        if currentQuantity < 0:
            return False
        else:
            # Perform update and return true
            ITEM_DB.update_one({'_id': item['_id']}, {"$set": {"quantity_active": int(currentQuantity)}})
            return True

def getUsers():
    result = []
    for item in USER_DB.find():
        result.append({
            "user_id": item["user_id"],
            "user_email": item["user_email"],
            "user_role": item["user_role"],
        })
    return result

def updateUserRole(user_id, new_role):
    USER_DB.update_one({'user_id': user_id}, {"$set": {
        "user_role": int(new_role)
    }})
    return

def insertHistory(eventType, user, event):
    currentDateTime = datetime.now(pytz.timezone('America/Los_Angeles'))
    timeString = currentDateTime.strftime("%H:%M:%S on %m/%d/%y")
    username = ""
    if user.is_authenticated:
        username = user.email
    else:
        ipAddress = ""
        if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
            ipAddress = str(request.environ['REMOTE_ADDR'])
        else:
            ipAddress = str(request.environ['HTTP_X_FORWARDED_FOR']) # if behind a proxy
        username = "guest - " + ipAddress
        
    HISTORY_DB.insert_one({
        "date": str(timeString).strip(),
        "type": str(eventType).strip(),
        "user": str(username).strip(),
        "event": str(event).strip(),
    })
    return

def getHistory():
    result = []
    for item in HISTORY_DB.find():
        result.append({
            "date": item["date"],
            "type": item["type"],
            "user": item["user"],
            "event": item["event"]
        })
    result.reverse()
    return result