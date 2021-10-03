from app import app
from flask_login import current_user
from flask import redirect, render_template

from app.database import db_interface as database

@app.route('/')
def index():
    return redirect('/dashboard')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', USER=current_user)

@app.route('/feedback')
def feedback():
    return render_template('feedback.html', USER=current_user)

@app.route('/ping')
def ping():
    return "healthy", 200