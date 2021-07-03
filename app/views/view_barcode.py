from app import app
from flask_login import current_user, login_required
from flask import render_template, redirect, request, flash

from app.database import db_interface as database
from app.register import Barcode_Lookup
from app.views import view_util

@app.route('/barcode/check_in', methods=['GET', 'POST'])
@login_required
def barcode_check_in_item():
    database.insert_history("PAGE_VISIT", current_user, "Viewed barcode checkin")
    if not view_util.validate_user():
        return view_util.returnPermissionError()

    form_barcode = Barcode_Lookup(request.form)
    if request.method == 'POST' and form_barcode.validate():
        if database.scan_barcode_update_quantity(form_barcode.barcode.data, form_barcode.quantity.data):
            item_id = database.get_barcode(form_barcode.barcode.data)['item_id']
            database.insert_history("EDIT", current_user, "Check in with barcode. Barcode: " + str(form_barcode.barcode.data) + ", Quantity: " + str(form_barcode.quantity.data))
            return redirect('/view/item/' + item_id)
        else:
            flash("An error occurred when handling your request. Please validate the barcode and quantity.")

    return render_template('scan:barcode.html', USER=current_user, form=form_barcode, action="Check in", defaultQuantity=1)

@app.route('/barcode/check_out', methods=['GET', 'POST'])
@login_required
def barcode_check_out_item():
    database.insert_history("PAGE_VISIT", current_user, "Viewed barcode checkout")
    if not view_util.validate_user():
        return view_util.returnPermissionError()

    form_barcode = Barcode_Lookup(request.form)
    if request.method == 'POST' and form_barcode.validate():
        if database.scan_barcode_update_quantity(form_barcode.barcode.data, form_barcode.quantity.data):
            item_id = database.get_barcode(form_barcode.barcode.data)['item_id']
            database.insert_history("EDIT", current_user, "Check out with barcode. Barcode: " + str(form_barcode.barcode.data) + ", Quantity: " + str(form_barcode.quantity.data))
            return redirect('/view/item/' + item_id)
        else:
            flash("An error occurred when handling your request. Please validate the barcode and quantity.")

    return render_template('scan:barcode.html', USER=current_user, form=form_barcode, action="Check out", defaultQuantity=-1)


@app.route('/barcode/lookup', methods=['GET', 'POST'])
def barcode_look_up_item():
    database.insert_history("PAGE_VISIT", current_user, "Viewed barcode lookup")
    form_barcode = Barcode_Lookup(request.form)
    if request.method == 'POST' and form_barcode.validate():
        item_id = database.get_barcode(form_barcode.barcode.data)['item_id']
        database.insert_history("EDIT", current_user, "Barcode lookup. Barcode: " + str(form_barcode.barcode.data))
        return redirect('/view/item/' + item_id)

    return render_template('scan:barcode.html', USER=current_user, form=form_barcode, action="Look up")
