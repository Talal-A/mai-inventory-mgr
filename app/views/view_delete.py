from app import app
from flask_login import current_user, login_required
from flask import render_template, redirect

from app.database import db_interface as database
from app.views import view_util

@app.route('/delete/barcode')
@login_required
def delete_barcode_view():
    database.insert_history("PAGE_VISIT", current_user, "Viewed delete barcode view.")
    if not view_util.validate_user():
        return view_util.returnPermissionError()
    return render_template('delete:barcode.html', USER=current_user, barcodes=database.get_all_barcodes())

@app.route('/delete/barcode/<string:uuid>')
@login_required
def delete_barcode(uuid):
    database.insert_history("PAGE_VISIT", current_user, "Viewed delete barcode.")
    if not view_util.validate_user():
        return view_util.returnPermissionError()
    database.delete_barcode(uuid)
    database.insert_history("DELETE", current_user, "Deleted barcode. UUID: " + str(uuid))
    return redirect('/delete/barcode')

@app.route('/delete/image')
@login_required
def delete_image_view():
    database.insert_history("PAGE_VISIT", current_user, "Viewed delete image view.")
    if not view_util.validate_user():
        return view_util.returnPermissionError()
    return render_template('delete:image.html', USER=current_user, images=database.get_all_images())

@app.route('/delete/image/<string:uuid>')
@login_required
def delete_image(uuid):
    database.insert_history("PAGE_VISIT", current_user, "Viewed delete image.")
    if not view_util.validate_user():
        return view_util.returnPermissionError()
    database.delete_image(uuid)
    database.insert_history("DELETE", current_user, "Deleted image. UUID: " + str(uuid))
    return redirect('/delete/image')

@app.route('/delete/item/<string:uuid>')
@login_required
def delete_item(uuid):
    database.insert_history("PAGE_VISIT", current_user, "Viewed delete item.")
    if not view_util.validate_admin():
        return view_util.returnPermissionError()
    database.delete_item(uuid)
    database.insert_history("DELETE", current_user, "Deleted item. UUID: " + str(uuid))
    return redirect('/view')

@app.route('/delete/category')
@login_required
def delete_category_view():
    database.insert_history("PAGE_VISIT", current_user, "Viewed delete category view.")
    if not view_util.validate_admin():
        return view_util.returnPermissionError()
    return render_template('delete:category.html', USER=current_user, categories=database.get_deletable_categories())

@app.route('/delete/category/<string:uuid>')
@login_required
def delete_category(uuid):
    database.insert_history("PAGE_VISIT", current_user, "Viewed delete category.")
    if not view_util.validate_admin():
        return view_util.returnPermissionError()
    database.delete_category(uuid)
    database.insert_history("DELETE", current_user, "Deleted category. UUID: " + str(uuid))
    return redirect('/delete/category')
