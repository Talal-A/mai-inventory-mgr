from app import app
from flask_login import current_user, login_required
from flask import render_template, redirect

from app.database import db_interface as database
from app.views import view_util

@app.route('/delete/image')
@login_required
def delete_image_view():
    if not view_util.validate_user():
        return view_util.returnPermissionError()
    return render_template('delete:image.html', USER=current_user, images=database.get_all_images())

@app.route('/delete/image/<string:uuid>')
@login_required
def delete_image(uuid):
    if not view_util.validate_user():
        return view_util.returnPermissionError()
    database.delete_image(uuid)
    return redirect('/delete/image')

@app.route('/delete/item/<string:uuid>')
@login_required
def delete_item(uuid):
    if not view_util.validate_user():
        return view_util.returnPermissionError()
    database.delete_item(uuid)
    return redirect('/view/item/' + uuid)

@app.route('/restore/item/<string:uuid>')
@login_required
def restore_item(uuid):
    if not view_util.validate_user():
        return view_util.returnPermissionError()
    database.restore_deleted_item(uuid)
    return redirect('/view/item/' + uuid)

@app.route('/delete/category')
@login_required
def delete_category_view():
    if not view_util.validate_admin():
        return view_util.returnPermissionError()
    return render_template('delete:category.html', USER=current_user, categories=database.get_deletable_categories())

@app.route('/delete/category/<string:uuid>')
@login_required
def delete_category(uuid):
    if not view_util.validate_admin():
        return view_util.returnPermissionError()
    database.delete_category(uuid)
    return redirect('/view/category/' + uuid)

@app.route('/restore/category/<string:uuid>')
@login_required
def restore_category(uuid):
    if not view_util.validate_admin():
        return view_util.returnPermissionError()
    database.restore_category(uuid)
    return redirect('/view/category/' + uuid)

@app.route('/delete/user/<string:uuid>')
@login_required
def delete_user(uuid):
    if not view_util.validate_admin():
        return view_util.returnPermissionError()
    database.update_user_role(uuid, -100)
    return redirect('/view/user/' + uuid)

@app.route('/restore/user/<string:uuid>')
@login_required
def restore_user(uuid):
    if not view_util.validate_admin():
        return view_util.returnPermissionError()
    database.update_user_role(uuid, 0)
    return redirect('/view/user/' + uuid)
