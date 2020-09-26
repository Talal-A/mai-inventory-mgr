# views.py

from flask import render_template, request, redirect
from wtforms import Form, StringField, validators, ValidationError, SubmitField, TextAreaField

from app import app
from .db import insertCategory, getCategories, getCategoryForId, updateCategory, insertItem, getItems, getItemForId, updateItem, getDeletableCategories, deleteCategory, insertBarcode, getBarcodesForItem, getBarcodes, deleteBarcode, getItemsForCategory, deleteItem, getBarcode, scanBarcodeAndUpdateQuantity
from .register import Register_Category, Register_Item, Update_Item, Register_Barcode, Barcode_Lookup

USERNAME="Talal"

@app.route('/')
def index():
    return redirect('/dashboard')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', USER=USERNAME)

@app.route('/feedback')
def feedback():
    return render_template('feedback.html', USER=USERNAME)

@app.route('/register/<string:type>', methods=['GET', 'POST'])
def register_with_param(type):
    form_category = Register_Category(request.form)
    form_item = Register_Item(request.form)
    form_barcode = Register_Barcode(request.form)

    if type == 'category':
        if request.method == 'POST' and form_category.category.data and form_category.validate():
            insertCategory(form_category.category.data)
            return redirect('/dashboard')

        return render_template('register:' + type + '.html', USER=USERNAME, form=form_category)

    elif type == 'item':
        if request.method == 'POST' and form_item.category.data and form_item.item.data and form_item.validate():
            insertItem(str(form_item.category.data).strip(), str(form_item.item.data).strip(), str(form_item.location.data).strip())
            return redirect('/dashboard')

        return render_template('register:' + type + '.html', USER=USERNAME, form=form_item, categories=getCategories())

    elif type == 'barcode':
        if request.method == 'POST' and form_barcode.validate():
            insertBarcode(str(form_barcode.barcode.data).strip(), str(form_barcode.item.data).strip())
            return redirect('/dashboard')

        return render_template('register:' + type + '.html', USER=USERNAME, form=form_barcode, categories=getCategories())

    else:
        return redirect('/dashboard')

@app.route('/edit/item/add_barcode/<string:uuid>', methods=['GET', 'POST'])
def register_barcode_for_item(uuid):
    form_barcode = Register_Barcode(request.form)
    form_barcode.item.data = str(uuid)
    form_barcode.item.render_kw = {'disabled':'disabled'}

    print(form_barcode.item.data)
    if request.method == 'POST' and form_barcode.validate():
        insertBarcode(str(form_barcode.barcode.data).strip(), str(form_barcode.item.data).strip())
        return redirect('/view/item/' + uuid)

    return render_template('register:' + 'barcode' + '.html', USER=USERNAME, form=form_barcode)

@app.route('/edit/category/<string:uuid>', methods=['GET', 'POST'])
def edit_category(uuid):
    form_category = Register_Category(request.form)

    if request.method == 'POST' and form_category.category.data and form_category.validate():
        updateCategory(uuid, form_category.category.data)
        return redirect('/view')
    else:
        form_category.category.data = getCategoryForId(uuid)['name']

    return render_template('edit:category.html', USER=USERNAME, form=form_category)

@app.route('/delete/barcode')
def delete_barcode_view():
    return render_template('delete:barcode.html', USER=USERNAME, barcodes=getBarcodes())

@app.route('/delete/barcode/<string:uuid>')
def delete_barcode(uuid):
    deleteBarcode(uuid)
    return redirect('/delete/barcode')

@app.route('/delete/item/<string:uuid>')
def delete_item(uuid):
    deleteItem(uuid)
    return redirect('/view')

@app.route('/delete/category')
def delete_category_view():
    return render_template('delete:category.html', USER=USERNAME, categories=getDeletableCategories())

@app.route('/delete/category/<string:uuid>')
def delete_category(uuid):
    deleteCategory(uuid)
    return redirect('/delete/category')

@app.route('/edit/item/<string:uuid>', methods=['GET', 'POST'])
def edit_item(uuid):
    form_item = Update_Item(request.form)

    if request.method == 'POST' and form_item.validate():
        updateItem(uuid, form_item.category.data, form_item.location.data, form_item.quantity_active.data, form_item.quantity_expired.data, form_item.notes.data, form_item.url.data)
        return redirect('/view/item/' + uuid)
    else:
        current_item = getItemForId(uuid)
        form_item.category.data = current_item['category_id']
        form_item.location.data = current_item['location']
        form_item.quantity_active.data = current_item['quantity_active']
        form_item.quantity_expired.data = current_item['quantity_expired']
        form_item.notes.data = current_item['notes']
        form_item.url.data = current_item['url']

    return render_template('edit:item.html', USER=USERNAME, form=form_item, item_name=current_item['name'])

@app.route('/view/category/<string:uuid>')
def view_category(uuid):
    return render_template('view:items.html', USER=USERNAME, category=getCategoryForId(uuid)['name'], items=getItemsForCategory(uuid))

@app.route('/view/all')
def view_all_items():
    return render_template('view:items.html', USER=USERNAME, category='All items', items=getItems())

@app.route('/view/item/<string:uuid>')
def view_item(uuid):
    return render_template('view:item.html', USER=USERNAME, item=getItemForId(uuid), barcodes=getBarcodesForItem(uuid))

@app.route('/view')
def view():
    return render_template('view.html', USER=USERNAME, categories=getCategories())

@app.route('/barcode/check_in', methods=['GET', 'POST'])
def barcode_check_in_item():
    form_barcode = Barcode_Lookup(request.form)
    if request.method == 'POST' and form_barcode.validate():
        print("okay...")
        print(form_barcode.quantity.data)
        if scanBarcodeAndUpdateQuantity(form_barcode.barcode.data, form_barcode.quantity.data):
            item_id = getBarcode(form_barcode.barcode.data)['item_id']
            return redirect('/view/item/' + item_id)

    return render_template('scan:barcode.html', USER=USERNAME, form=form_barcode, action="Check in", defaultQuantity=1)

@app.route('/barcode/check_out', methods=['GET', 'POST'])
def barcode_check_out_item():
    form_barcode = Barcode_Lookup(request.form)
    if request.method == 'POST' and form_barcode.validate():
        if scanBarcodeAndUpdateQuantity(form_barcode.barcode.data, form_barcode.quantity.data):
            item_id = getBarcode(form_barcode.barcode.data)['item_id']
            return redirect('/view/item/' + item_id)

    return render_template('scan:barcode.html', USER=USERNAME, form=form_barcode, action="Check out", defaultQuantity=-1)

@app.route('/barcode/lookup', methods=['GET', 'POST'])
def barcode_look_up_item():
    form_barcode = Barcode_Lookup(request.form)
    if request.method == 'POST' and form_barcode.validate():
        item_id = getBarcode(form_barcode.barcode.data)['item_id']
        return redirect('/view/item/' + item_id)

    return render_template('scan:barcode.html', USER=USERNAME, form=form_barcode, action="Look up")
