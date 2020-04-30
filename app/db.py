import pymongo

myclient = pymongo.MongoClient("mongodb://nerv:9201/")
mydb = myclient["MAI_UCLA_DB"]

CATEGORY_DB = mydb["category"]

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

def insertCategory(newCategory):
	if str(newCategory) not in getCategoryNames():
		CATEGORY_DB.insert_one({"name": str(newCategory).strip()})
