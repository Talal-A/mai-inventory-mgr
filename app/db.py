import pymongo

myclient = pymongo.MongoClient("mongodb://nerv:9201/")
mydb = myclient["MAI_UCLA_DB"]

CATEGORY_DB = mydb["category"]

def getCategories():
	result = []
	for item in CATEGORY_DB.find():
		result.append(item['name'])
	return result

def insertCategory(newCategory):
	print(getCategories())
	if str(newCategory) not in getCategories():
		CATEGORY_DB.insert_one({"name": str(newCategory).strip()})
