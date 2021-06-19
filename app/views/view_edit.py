from app import app
from flask_login import current_user, login_required
from flask import render_template, request, redirect

from app.database import db_interface as database
from app.register import Register_Barcode, Register_Category, Update_Item
from app.views import view_util

import requests
import config

@app.route('/edit/item/add_barcode/<string:uuid>', methods=['GET', 'POST'])
@login_required
def register_barcode_for_item(uuid):
    print("HELLO??")
    database.insert_history("PAGE_VISIT", current_user, "Viewed register barcode.")
    if not view_util.validate_user():
        return view_util.returnPermissionError()

    form_barcode = Register_Barcode(request.form)
    form_barcode.item.data = str(uuid)
    form_barcode.item.render_kw = {'disabled':'disabled'}

    print(form_barcode.item.data)
    if request.method == 'POST' and form_barcode.validate():
        database.insert_barcode(str(form_barcode.barcode.data).strip(), str(form_barcode.item.data).strip())
        database.insert_history("REGISTER", current_user, "Registered barcode. Item: " + str(form_barcode.item.data).strip() + ", Barcode: " + str(form_barcode.barcode.data).strip())
        return redirect('/view/item/' + uuid)

    return render_template('register:' + 'barcode' + '.html', USER=current_user, form=form_barcode)

@app.route('/edit/item/add_barcode', methods=['GET', 'POST'])
@login_required
def register_barcode():
    database.insert_history("PAGE_VISIT", current_user, "Viewed register barcode.")
    if not view_util.validate_user():
        return view_util.returnPermissionError()

    form_barcode = Register_Barcode(request.form)

    if request.method == 'POST' and form_barcode.validate():
        database.insert_barcode(str(form_barcode.barcode.data).strip(), str(form_barcode.item.data).strip())
        database.insert_history("REGISTER", current_user, "Registered barcode. Item: " + str(form_barcode.item.data).strip() + ", Barcode: " + str(form_barcode.barcode.data).strip())
        return redirect('/view/item/' + str(form_barcode.item.data).strip())

    return render_template('register:' + 'barcode' + '.html', USER=current_user, form=form_barcode)

@app.route('/edit/item/upload_photo/<string:uuid>', methods=['POST'])
@login_required
def upload_photo_for_item(uuid):
    database.insert_history("PAGE_VISIT", current_user, "Uploaded image for item.")
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
        return str(success)
    except:
        return str(False)

@app.route('/edit/category/<string:uuid>', methods=['GET', 'POST'])
@login_required
def edit_category(uuid):
    database.insert_history("PAGE_VISIT", current_user, "Viewed edit category.")
    if not view_util.validate_user():
        return view_util.returnPermissionError()

    form_category = Register_Category(request.form)

    if request.method == 'POST' and form_category.category.data and form_category.validate():
        database.update_category_name(uuid, form_category.category.data)
        database.insert_history("EDIT", current_user, "Updated category. UUID: " + str(uuid).strip() + ", Category: " + str(form_category.category.data).strip())
        return redirect('/view')
    else:
        form_category.category.data = database.get_category(uuid)['name']

    return render_template('edit:category.html', USER=current_user, form=form_category)

@app.route('/edit/item/<string:uuid>', methods=['GET', 'POST'])
@login_required
def edit_item(uuid):
    database.insert_history("PAGE_VISIT", current_user, "Viewed edit item.")
    if not view_util.validate_user():
        return view_util.returnPermissionError()

    form_item = Update_Item(request.form)

    if request.method == 'POST' and form_item.validate():
        database.update_item(uuid, form_item.category.data, form_item.location.data, form_item.quantity_active.data, form_item.quantity_expired.data, form_item.notes.data, form_item.url.data)
        database.insert_history("EDIT", current_user, "Edited item. UUID: " + str(uuid) + ", Category: " + str(form_item.category.data) + ", Location: " + str(form_item.location.data) + ", Quantity_Active: " + str(form_item.quantity_active.data) + ", Quantity Expired: " + str(form_item.quantity_expired.data) + ", Notes: " + str(form_item.notes.data) + ", URL: " + str(form_item.url.data))
        return redirect('/view/item/' + uuid)
    else:
        current_item = database.get_item(uuid)
        form_item.category.data = current_item['category_id']
        form_item.location.data = current_item['location']
        form_item.quantity_active.data = current_item['quantity_active']
        form_item.quantity_expired.data = current_item['quantity_expired']
        form_item.notes.data = current_item['notes']
        form_item.url.data = current_item['url']

    return render_template('edit:item.html', USER=current_user, form=form_item, item_name=current_item['name'])
