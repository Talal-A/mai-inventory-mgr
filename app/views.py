# views.py

from flask import render_template, request, redirect
from wtforms import Form, StringField, validators, ValidationError, SubmitField, TextAreaField

from app import app
from .db import insertCategory
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
    print(type)
    return render_template('register.html', USER=USERNAME)

@app.route('/register/<string:type>', methods=['GET', 'POST'])
def register_with_param(type):
    form_category = Register_Category(request.form)

    if request.method == 'POST' and form_category.category.data and form_category.validate():
        insertCategory(form_category.category.data)

    return render_template('register:' + type + '.html', USER=USERNAME, form=form_category)