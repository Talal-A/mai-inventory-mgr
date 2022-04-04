from app import app
from flask_login import current_user, login_required
from flask import render_template, request, g
from app.database import db_interface as database
from . import view_util
import logging
import time 

@app.before_request
def before_request():
    g.start = time.time()
    logging.info("Page entry: " + database.get_username(current_user) + " visited " + request.path)

@app.teardown_request
def teardown_request(exception=None):
    diff_ms = (time.time() - g.start) * 1000
    database.insert_latency_log(request.path, diff_ms)

@app.route('/view')
def view():
    return render_template('view.html', USER=current_user, categories=database.get_all_active_categories())

@app.route('/view/users')
@login_required
def view_all_users():
    if not view_util.validate_admin():
        return view_util.returnPermissionError()
    return render_template('view:users.html', USER=current_user, users=database.get_all_users())

@app.route('/view/user/<string:uuid>')
@login_required
def view_user(uuid):
    if not view_util.validate_admin():
        return view_util.returnPermissionError()
    return render_template('view:user.html', USER=current_user, user=database.get_user(uuid))

@app.route('/view/audit')
def view_audit():
    if not view_util.validate_admin():
        return view_util.returnPermissionError()

    return render_template('audit.html', USER=current_user, events=database.get_all_audit())

@app.route('/view/all')
def view_all_items():
    return render_template('view:items.html', USER=current_user, category='All items', items=database.get_all_items())

@app.route('/view/deleted_categories')
def view_all_deleted_categories():
    if not view_util.validate_admin():
        return view_util.returnPermissionError()
    return render_template('view.html', USER=current_user, categories=database.get_all_deleted_categories())

@app.route('/view/deleted')
def view_all_deleted_items():
    if not view_util.validate_user():
        return view_util.returnPermissionError()
    return render_template('view:items.html', USER=current_user, category='Deleted items', items=database.get_all_deleted_items())

@app.route('/view/category/<string:uuid>')
def view_category(uuid):
    return render_template('view:items.html', USER=current_user, category=database.get_category(uuid)['name'], items=database.get_all_items_for_category(uuid))


@app.route('/view/item/<string:uuid>')
def view_item(uuid):
    return render_template('view:item.html', USER=current_user, item=database.get_item(uuid), barcodes=database.get_barcodes_for_item(uuid), images=database.get_all_images_for_item(uuid), audit=database.get_item_audit(uuid))
