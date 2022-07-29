from app import app
from flask_login import current_user, login_required
from flask import render_template, request, redirect

from app.database import db_interface as database
from app.register import Register_Barcode, Register_Category, Update_Item
from app.views import view_util

import requests
import config
import logging

@app.route('/edit/item/add_barcode/<string:uuid>', methods=['GET', 'POST'])
@login_required
def register_barcode_for_item(uuid):
    if not view_util.validate_user():
        return view_util.returnPermissionError()

    form_barcode = Register_Barcode(request.form)
    form_barcode.item.data = str(uuid)
    form_barcode.item.render_kw = {'disabled':'disabled'}

    if request.method == 'POST' and form_barcode.validate():
        database.insert_barcode(str(form_barcode.barcode.data).strip(), str(form_barcode.item.data).strip())
        return redirect('/view/item/' + uuid)

    return render_template('register:' + 'barcode' + '.html', USER=current_user, form=form_barcode)

@app.route('/edit/item/add_barcode', methods=['GET', 'POST'])
@login_required
def register_barcode():
    if not view_util.validate_user():
        return view_util.returnPermissionError()

    form_barcode = Register_Barcode(request.form)

    if request.method == 'POST' and form_barcode.validate():
        database.insert_barcode(str(form_barcode.barcode.data).strip(), str(form_barcode.item.data).strip())
        return redirect('/view/item/' + str(form_barcode.item.data).strip())

    return render_template('register:' + 'barcode' + '.html', USER=current_user, form=form_barcode)

@app.route('/edit/item/upload_photo/<string:uuid>', methods=['POST'])
@login_required
def upload_photo_for_item(uuid):
    if not view_util.validate_user():
        return view_util.returnPermissionError()

    try:
        result = requests.post(
            url='https://api.imgur.com/3/image',
            data={'image': request.get_json()['img'].split(',')[1]},
            headers={'Authorization': 'Client-ID ' + config.IMGUR_CLIENT_ID}
            ).json()
        image_url = result['data']['link']
        delete_hash = result['data']['deletehash']
        success = result['success']
        if success:
            database.insert_image(image_url, delete_hash, uuid)
        else:
            logging.error("An error occurred while uploading image: " + str(result))
        return str(success)
    except Exception as e:
        logging.error(e)
        return str(False)

@app.route('/edit/category/<string:uuid>', methods=['GET', 'POST'])
@login_required
def edit_category(uuid):
    if not view_util.validate_user():
        return view_util.returnPermissionError()

    form_category = Register_Category(request.form)

    if request.method == 'POST' and form_category.category.data and form_category.validate():
        database.update_category_name(uuid, form_category.category.data)
        return redirect('/view')
    else:
        form_category.category.data = database.get_category(uuid)['name']

    return render_template('edit:category.html', USER=current_user, form=form_category)

@app.route('/edit/item/<string:uuid>', methods=['GET', 'POST'])
@login_required
def edit_item(uuid):
    if not view_util.validate_user():
        return view_util.returnPermissionError()

    form_item = Update_Item(request.form)

    if request.method == 'POST' and form_item.validate():
        database.update_item(uuid, form_item.name.data, form_item.category.data, form_item.location.data, form_item.quantity_active.data, form_item.quantity_expired.data, form_item.notes_public.data, form_item.url.data, form_item.notes_private.data)
        return redirect('/view/item/' + uuid)
    else:
        current_item = database.get_item(uuid)
        form_item.name.data = current_item['name']
        form_item.category.data = current_item['category_id']
        form_item.location.data = current_item['location']
        form_item.quantity_active.data = current_item['quantity_active']
        form_item.quantity_expired.data = current_item['quantity_expired']
        form_item.notes_public.data = current_item['notes_public']
        form_item.notes_private.data = current_item['notes_private']
        form_item.url.data = current_item['url']

    return render_template('edit:item.html', USER=current_user, form=form_item, item_name=current_item['name'])
