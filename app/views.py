# views.py

from flask import render_template, request, redirect
from wtforms import Form, StringField, validators, ValidationError, SubmitField, TextAreaField

from app import app
from .db import insertCategory, getCategories, getCategoryForId, updateCategory, insertItem, getItems, getItemForId, updateItem, getDeletableCategories, deleteCategory, insertBarcode, getBarcodesForItem, getBarcodes, deleteBarcode, getItemsForCategory, deleteItem
from .register import Register_Category, Register_Item, Update_Item, Register_Barcode

USERNAME="Talal"

@app.route('/')
def index():
    return redirect('/dashboard')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', USER=USERNAME)

@app.route('/register/<string:type>', methods=['GET', 'POST'])
def register_with_param(type):
    form_category = Register_Category(request.form)
    form_item = Register_Item(request.form)
    form_barcode = Register_Barcode(request.form)

    if type == 'category':
        if request.method == 'POST' and form_category.category.data and form_category.validate():
            insertCategory(form_category.category.data)
            return redirect('/register')

        return render_template('register:' + type + '.html', USER=USERNAME, form=form_category)

    elif type == 'item':
        if request.method == 'POST' and form_item.category.data and form_item.item.data and form_item.validate():
            insertItem(str(form_item.category.data).strip(), str(form_item.item.data).strip(), str(form_item.location.data).strip())
            return redirect('/register')

        return render_template('register:' + type + '.html', USER=USERNAME, form=form_item, categories=getCategories())

    elif type == 'barcode':
        if request.method == 'POST' and form_barcode.validate():
            insertBarcode(str(form_barcode.barcode.data).strip(), str(form_barcode.item.data).strip())
            return redirect('/register')

        return render_template('register:' + type + '.html', USER=USERNAME, form=form_barcode, categories=getCategories())

    else:
        return redirect('/dashboard')

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
        updateItem(uuid, form_item.category.data, form_item.location.data, form_item.quantity_active.data, form_item.quantity_expired.data, form_item.notes.data)
        return redirect('/view/item/' + uuid)
    else:
        current_item = getItemForId(uuid)
        form_item.category.data = current_item['category_id']
        form_item.location.data = current_item['location']
        form_item.quantity_active.data = current_item['quantity_active']
        form_item.quantity_expired.data = current_item['quantity_expired']
        form_item.notes.data = current_item['notes']

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
