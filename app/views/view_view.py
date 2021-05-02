from app import app
from flask_login import current_user, login_required
from flask import render_template

from app.database import db_interface as database
from . import view_util

@app.route('/view')
def view():
    database.insert_history("PAGE_VISIT", current_user, "Viewed /view")
    return render_template('view.html', USER=current_user, categories=database.get_all_categories())

@app.route('/view/users')
@login_required
def view_users():
    database.insert_history("PAGE_VISIT", current_user, "Viewed users page")
    if not view_util.validate_admin():
        return view_util.returnPermissionError()
    return render_template('view:users.html', USER=current_user, users=database.get_all_users())

@app.route('/view/history')
def view_history():
    database.insert_history("PAGE_VISIT", current_user, "Viewed history lookup")
    if not view_util.validate_admin():
        return view_util.returnPermissionError()

    return render_template('history.html', USER=current_user, events=database.get_history())

@app.route('/view/all')
def view_all_items():
    database.insert_history("PAGE_VISIT", current_user, "Viewed all items page")
    return render_template('view:items.html', USER=current_user, category='All items', items=database.get_all_items())

@app.route('/view/category/<string:uuid>')
def view_category(uuid):
    database.insert_history("PAGE_VISIT", current_user, "Viewed category " + str(uuid))
    return render_template('view:items.html', USER=current_user, category=database.get_category(uuid)['name'], items=database.get_all_items_for_category(uuid))


@app.route('/view/item/<string:uuid>')
def view_item(uuid):
    database.insert_history("PAGE_VISIT", current_user, "Viewed item " + str(uuid))
    return render_template('view:item.html', USER=current_user, item=database.get_item(uuid), barcodes=database.get_barcodes_for_item(uuid), images=database.get_all_images_for_item(uuid), audit=database.get_item_audit(uuid))
