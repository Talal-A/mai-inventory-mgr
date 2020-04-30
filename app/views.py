# views.py

from flask import render_template, request, redirect
from wtforms import Form, StringField, validators, ValidationError, SubmitField, TextAreaField

from app import app
from .db import insertCategory, getCategories, getCategoryForId, updateCategory
from .register import Register_Category

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

    if request.method == 'POST' and form_category.category.data and form_category.validate():
        insertCategory(form_category.category.data)
        return view()

    return render_template('register:' + type + '.html', USER=USERNAME, form=form_category)

@app.route('/edit/category/<string:uuid>', methods=['GET', 'POST'])
def edit_category(uuid):
    form_category = Register_Category(request.form)


    if request.method == 'POST' and form_category.category.data and form_category.validate():
        updateCategory(uuid, form_category.category.data)
        return redirect('/view')
    else:
        form_category.category.data = getCategoryForId(uuid)['name']

    return render_template('edit:category.html', USER=USERNAME, form=form_category)

@app.route('/view')
def view():
    print(getCategories())
    return render_template('view.html', USER=USERNAME, categories=getCategories())
