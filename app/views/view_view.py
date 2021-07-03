from app import app
from flask_login import current_user, login_required
from flask import render_template, request

from app.database import db_interface as database
from . import view_util
import logging

@app.before_request
def before_request():
    logging.info("Page entry: " + database.get_username(current_user) + " visited " + request.path)
    database.insert_history('PAGE_ENTRY', current_user, request.path)

@app.route('/view')
def view():
    return render_template('view.html', USER=current_user, categories=database.get_all_categories())

@app.route('/view/users')
@login_required
def view_users():
    if not view_util.validate_admin():
        return view_util.returnPermissionError()
    return render_template('view:users.html', USER=current_user, users=database.get_all_users())

@app.route('/view/history')
def view_history():
    if not view_util.validate_admin():
        return view_util.returnPermissionError()

    return render_template('history.html', USER=current_user, events=database.get_history())

@app.route('/view/all')
def view_all_items():
    return render_template('view:items.html', USER=current_user, category='All items', items=database.get_all_items())

@app.route('/view/deleted')
def view_all_deleted_items():
    if not view_util.validate_admin():
        return view_util.returnPermissionError()
    return render_template('view:items.html', USER=current_user, category='Deleted items', items=database.get_all_deleted_items())

@app.route('/view/category/<string:uuid>')
def view_category(uuid):
    return render_template('view:items.html', USER=current_user, category=database.get_category(uuid)['name'], items=database.get_all_items_for_category(uuid))


@app.route('/view/item/<string:uuid>')
def view_item(uuid):
    return render_template('view:item.html', USER=current_user, item=database.get_item(uuid), barcodes=database.get_barcodes_for_item(uuid), images=database.get_all_images_for_item(uuid), audit=database.get_item_audit(uuid))
