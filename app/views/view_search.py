from app import app
from flask_login import current_user, login_required
from flask import render_template, redirect, request, flash

from app.database import db_interface as database
from app.register import Search_QuantityUpdate
from app.views import view_util

@app.route('/search/check_out', methods=['GET', 'POST'])
@login_required
def search_check_out_item():
    database.insert_history("PAGE_VISIT", current_user, "Viewed search checkout")
    if not view_util.validate_user():
        return view_util.returnPermissionError()
    
    form_search = Search_QuantityUpdate(request.form)

    if request.method == 'POST' and form_search.validate():
        if database.search_item_update_quantity(form_search.selectInput.data, form_search.quantity.data):
            database.insert_history("EDIT", current_user, "Check out with search. ItemId: " + str(form_search.selectInput.data) + ", Quantity: " + str(form_search.quantity.data))
            return redirect('/view/item/' + form_search.selectInput.data)
        else:
            flash("An error occurred when handling your request. Please validate the selection and quantity.")

    return render_template('search:updateqty.html', USER=current_user, form=form_search, action="Check out", defaultQuantity=-1)

@app.route('/search/check_in', methods=['GET', 'POST'])
@login_required
def search_check_in_item():
    database.insert_history("PAGE_VISIT", current_user, "Viewed search checkin")
    if not view_util.validate_user():
        return view_util.returnPermissionError()
    
    form_search = Search_QuantityUpdate(request.form)

    if request.method == 'POST' and form_search.validate():
        if database.search_item_update_quantity(form_search.selectInput.data, form_search.quantity.data):
            database.insert_history("EDIT", current_user, "Check in with search. ItemId: " + str(form_search.selectInput.data) + ", Quantity: " + str(form_search.quantity.data))
            return redirect('/view/item/' + form_search.selectInput.data)
        else:
            flash("An error occurred when handling your request. Please validate the selection and quantity.")

    return render_template('search:updateqty.html', USER=current_user, form=form_search, action="Check in", defaultQuantity=1)
