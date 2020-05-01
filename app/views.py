# views.py

from flask import render_template, request, redirect
from wtforms import Form, StringField, validators, ValidationError, SubmitField, TextAreaField

from app import app
from .db import insertCategory, getCategories, getCategoryForId, updateCategory, insertItem, getItems, getItemForId
from .register import Register_Category, Register_Item, Update_Item

USERNAME="Talal"

@app.route('/')
def index():
    return redirect('/dashboard')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', USER=USERNAME)

@app.route('/register')
def register():
    return render_template('register.html', USER=USERNAME)

@app.route('/register/<string:type>', methods=['GET', 'POST'])
def register_with_param(type):
    form_category = Register_Category(request.form)
    form_item = Register_Item(request.form)

    if type == 'category':
        if request.method == 'POST' and form_category.category.data and form_category.validate():
            insertCategory(form_category.category.data)
            return redirect('/view')

        return render_template('register:' + type + '.html', USER=USERNAME, form=form_category)

    elif type == 'item':
        if request.method == 'POST' and form_item.category.data and form_item.item.data and form_item.validate():
            insertItem(str(form_item.category.data).strip(), str(form_item.item.data).strip(), str(form_item.location.data).strip())
            return redirect('/view')

        return render_template('register:' + type + '.html', USER=USERNAME, form=form_item, categories=getCategories())

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

@app.route('/edit/item/<string:uuid>', methods=['GET', 'POST'])
def edit_item(uuid):
    form_item = Update_Item(request.form)

    if request.method == 'POST' and form_item.item.data and form_item.validate():
        # updateCategory(uuid, form_category.category.data)
        return redirect('/view')
    else:
        current_item = getItemForId(uuid)
        print(current_item)
        form_item.category.data = current_item['category_id']
        form_item.quantity_active.data = current_item['quantity_active']
        form_item.quantity_expired.data = current_item['quantity_expired']

    return render_template('edit:item.html', USER=USERNAME, form=form_item, item_name=current_item['name'])

@app.route('/view')
def view():
    print(getCategories())
    print(getItems())
    return render_template('view.html', USER=USERNAME, categories=getCategories(), items=getItems())
