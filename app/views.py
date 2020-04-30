# views.py

from flask import render_template, request, redirect
from app import app

@app.route('/')
def index():
    return redirect('/dashboard')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', USER="Talal")
