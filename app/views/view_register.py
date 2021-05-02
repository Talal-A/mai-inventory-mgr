from app import app
from flask_login import current_user, login_required
from flask import render_template, redirect, request

from app.database import db_interface as database
from app.register import Register_Category, Register_Barcode, Register_Item
from app.views import view_util

@app.route('/register/<string:type>', methods=['GET', 'POST'])
@login_required
def register_with_param(type):
    database.insert_history("PAGE_VISIT", current_user, "Viewed register.")
    if not view_util.validate_user():
        return view_util.returnPermissionError()
    form_category = Register_Category(request.form)
    form_item = Register_Item(request.form)
    form_barcode = Register_Barcode(request.form)

    if type == 'category':
        if not view_util.validate_admin():
            return view_util.returnPermissionError()

        if request.method == 'POST' and form_category.category.data and form_category.validate():
            database.insert_category(form_category.category.data)
            database.insert_history("REGISTER", current_user, "Registered category: " + str(form_category.category.data))
            return redirect('/dashboard')

        return render_template('register:' + type + '.html', USER=current_user, form=form_category)

    elif type == 'item':
        if request.method == 'POST' and form_item.category.data and form_item.item.data and form_item.validate():
            database.insert_item(str(form_item.category.data).strip(), str(form_item.item.data).strip(), str(form_item.location.data).strip())
            database.insert_history("REGISTER", current_user, "Registered item. Category: " + str(form_item.category.data).strip() + ", Item: " + str(form_item.item.data).strip() + ", Location: " + str(form_item.location.data).strip())
            return redirect('/dashboard')

        return render_template('register:' + type + '.html', USER=current_user, form=form_item, categories=database.get_all_categories())

    elif type == 'barcode':
        if request.method == 'POST' and form_barcode.validate():
            database.insert_barcode(str(form_barcode.barcode.data).strip(), str(form_barcode.item.data).strip())
            database.insert_history("REGISTER", current_user, "Registered barcode. Item: " + str(form_barcode.item.data).strip() + ", Barcode: " + str(form_barcode.barcode.data).strip())
            return redirect('/dashboard')

        return render_template('register:' + type + '.html', USER=current_user, form=form_barcode, categories=database.get_all_categories())

    else:
        return redirect('/dashboard')


