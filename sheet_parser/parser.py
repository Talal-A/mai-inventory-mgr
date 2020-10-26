# Takes in the HTML sheet as well as the CSV of the sheet.

import sys
from bs4 import BeautifulSoup
import csv
import pymongo
from bson.objectid import ObjectId
sys.path.append('/Users/talal/dev/mai-ucla-2/app/')

import db

print("Running sheet parser on inputs:")
print('Argument List:', str(sys.argv))

HTML_INPUT = str(sys.argv[1])
TSV_INPUT = str(sys.argv[2])

print("Beginning analysis of HTML file: " + HTML_INPUT)

html_file = open(HTML_INPUT)
soup = BeautifulSoup(html_file, 'html.parser')

count = 0

urlDict = {}

for a in soup.find_all('a', href=True):
    count += 1
    item = str(a.contents[0]).strip()
    url = str(a['href']).strip()
    urlDict[item] = url

print("URLs found:" , count)

print("Beginning analysis of TSV file: " + TSV_INPUT)

tsv_file = open(TSV_INPUT)
rowCount = 0
results = []
for line in tsv_file.readlines():        
    rowCount += 1
    if rowCount == 1:
        print("Skipping row 1..")
        continue
    
    lineItem = line.split("\t")
    category = str(lineItem[0]).strip()
    location = str(lineItem[1]).strip()
    itemName = str(lineItem[2]).strip()
    itemUrl = urlDict.get(itemName, "")

    try:
        quantity = int(str(lineItem[3]).strip().replace(",", ""))
    except ValueError:
        quantity = 0

    try:
        exp_quantity = int(str(lineItem[4]).strip().replace(",", ""))
    except ValueError:
        exp_quantity = 0

    notes = str(lineItem[5])

    barcodes = []
    barcodes.append(str(lineItem[6]).strip())
    barcodes.append(str(lineItem[7]).strip())
    barcodes.append(str(lineItem[8]).strip())
    barcodes.append(str(lineItem[9]).strip())
    barcodes.append(str(lineItem[10]).strip())
    barcodes.append(str(lineItem[11]).strip())
    barcodes.append(str(lineItem[12]).strip())

    # Clean up barcodes, remove empty.
    barcodes = list(filter((lambda x : x != ""), barcodes))
    results.append({
        "category": category, 
        "location": location,
        "name": itemName,
        "url": itemUrl,
        "quantity": quantity,
        "exp_quantity": exp_quantity,
        "notes": notes,
        "barcodes": barcodes
        })

print("Total results: " + str(len(results)))
print("Total rows: " + str(rowCount))
html_file.close()
tsv_file.close()


for item in results:
    # Create the category
    db.insertCategory(item["category"])

    # Get the category id
    categoryId = ""
    for cat in db.getCategories():
        if cat["name"] == item["category"]:
            categoryId = cat["id"]

    # Insert the item
    result = db.insertItem(categoryId, item["name"], item["location"], item["quantity"], item["exp_quantity"], item["notes"], item["url"])

    # Get the item id
    itemId = result.inserted_id

    # Insert the barcodes
    for barcode in item["barcodes"]:
        db.insertBarcode(barcode, itemId)
    
