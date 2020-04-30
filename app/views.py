# views.py

from flask import render_template, request, redirect
from app import app

@app.route('/')
def index():
    print('hello world')
    return "hello world"
