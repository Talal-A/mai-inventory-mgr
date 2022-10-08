from app import app
from flask_login import current_user, login_required
from flask import render_template, redirect, request

from app.database import db_interface as database
from app.register import Register_Category, Update_Item
from app.views import view_util

@app.route('/register/<string:type>', methods=['GET', 'POST'])
@login_required
def register_with_param(type):
    if not view_util.validate_user():
        return view_util.returnPermissionError()
    form_category = Register_Category(request.form)
    form_item = Update_Item(request.form)

    if type == 'category':
        if not view_util.validate_admin():
            return view_util.returnPermissionError()

        if request.method == 'POST' and form_category.category.data and form_category.validate():
            database.insert_category(form_category.category.data)
            return redirect('/dashboard')

        return render_template('register:' + type + '.html', USER=current_user, form=form_category)

    elif type == 'item':
        if request.method == 'POST' and form_item.category.data and form_item.name.data and form_item.validate():
            database.insert_item(form_item.category.data, form_item.name.data, form_item.location.data, form_item.quantity_active.data, form_item.quantity_expired.data, form_item.notes_public.data, form_item.url.data, form_item.notes_private.data)
            return redirect('/dashboard')        
        return render_template('register:' + type + '.html', USER=current_user, form=form_item, categories=database.get_all_active_categories())

    else:
        return redirect('/dashboard')


