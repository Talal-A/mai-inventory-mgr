# views.py

from flask import render_template, request, redirect
from app import app

@app.route('/')
def index():
    return redirect('/dashboard')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', USER="Talal")

@app.route('/register')
def register():
    print(type)
    return render_template('register.html', USER="Talal")

@app.route('/register/<string:type>')
def register_with_param(type):
    print(type)
    return render_template('register:' + type + '.html', USER="Talal")