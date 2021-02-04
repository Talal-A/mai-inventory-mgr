# views.py

from flask import render_template, request, redirect, flash
from wtforms import Form, StringField, validators, ValidationError, SubmitField, TextAreaField

from app import app
from .register import Register_Category, Register_Item, Update_Item, Register_Barcode, Barcode_Lookup, Search_QuantityUpdate
from . import database
import requests
import base64

from oauthlib.oauth2 import WebApplicationClient
import os 
import json

from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)

from .user import User

# WIP AUTH
GOOGLE_CLIENT_ID = os.environ.get("MAI_GOOGLE_CLIENT_ID", None)
GOOGLE_CLIENT_SECRET = os.environ.get("MAI_GOOGLE_CLIENT_SECRET", None)
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()


client = WebApplicationClient(GOOGLE_CLIENT_ID)

def validate_user():
    return current_user.is_authenticated and current_user.role >= 5

def validate_admin():
    return current_user.is_authenticated and current_user.role >= 10

def returnPermissionError():
    database.insert_history("PERMISSION_ERROR", current_user, "Attempted to access an unauthorized resource.")
    return "Error: you do not have permission to access this resource.", 401

# END WIP AUTH

@app.route('/')
def index():
    database.insert_history("PAGE_VISIT", current_user, "Viewed index.")
    return redirect('/dashboard')

@app.route('/login')
def login():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

@app.route('/login/callback')
def login_callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")

    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send a request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that you have tokens (yay) let's find and hit the URL
    # from Google that gives you the user's profile information,
    # including their Google profile image and email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # You want to make sure their email is verified.
    # The user authenticated with Google, authorized your
    # app, and now you've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        users_name = userinfo_response.json()["given_name"]

        user = User.get(unique_id)
        if not user:
            User.create(unique_id, users_name, users_email, 0)
            user = User(id_=unique_id, name=users_name, email=users_email, role=0)

        login_user(user)
        database.insert_history("LOGIN", user, "Logged in.")
    else:
        return "User email not available or not verified by Google.", 400

    return redirect('/dashboard')

@app.route('/logout')
@login_required
def logout():
    database.insert_history("LOGOUT", current_user, "Logged out.")
    logout_user()
    return redirect('/dashboard')

@app.route('/dashboard')
def dashboard():
    database.insert_history("PAGE_VISIT", current_user, "Viewed dashboard.")
    return render_template('dashboard.html', USER=current_user)

@app.route('/feedback')
def feedback():
    database.insert_history("PAGE_VISIT", current_user, "Viewed feedback.")
    return render_template('feedback.html', USER=current_user)

@app.route('/register/<string:type>', methods=['GET', 'POST'])
@login_required
def register_with_param(type):
    database.insert_history("PAGE_VISIT", current_user, "Viewed register.")
    if not validate_user():
        return returnPermissionError()
    form_category = Register_Category(request.form)
    form_item = Register_Item(request.form)
    form_barcode = Register_Barcode(request.form)

    if type == 'category':
        if not validate_admin():
            return returnPermissionError()

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

@app.route('/edit/item/add_barcode/<string:uuid>', methods=['GET', 'POST'])
@login_required
def register_barcode_for_item(uuid):
    database.insert_history("PAGE_VISIT", current_user, "Viewed register barcode.")
    if not validate_user():
        return returnPermissionError()

    form_barcode = Register_Barcode(request.form)
    form_barcode.item.data = str(uuid)
    form_barcode.item.render_kw = {'disabled':'disabled'}

    print(form_barcode.item.data)
    if request.method == 'POST' and form_barcode.validate():
        database.insert_barcode(str(form_barcode.barcode.data).strip(), str(form_barcode.item.data).strip())
        database.insert_history("REGISTER", current_user, "Registered barcode. Item: " + str(form_barcode.item.data).strip() + ", Barcode: " + str(form_barcode.barcode.data).strip())
        return redirect('/view/item/' + uuid)

    return render_template('register:' + 'barcode' + '.html', USER=current_user, form=form_barcode)

@app.route('/edit/category/<string:uuid>', methods=['GET', 'POST'])
@login_required
def edit_category(uuid):
    database.insert_history("PAGE_VISIT", current_user, "Viewed edit category.")
    if not validate_user():
        return returnPermissionError()

    form_category = Register_Category(request.form)

    if request.method == 'POST' and form_category.category.data and form_category.validate():
        database.update_category_name(uuid, form_category.category.data)
        database.insert_history("EDIT", current_user, "Updated category. UUID: " + str(uuid).strip() + ", Category: " + str(form_category.category.data).strip())
        return redirect('/view')
    else:
        form_category.category.data = database.get_category(uuid)['name']

    return render_template('edit:category.html', USER=current_user, form=form_category)

@app.route('/delete/barcode')
@login_required
def delete_barcode_view():
    database.insert_history("PAGE_VISIT", current_user, "Viewed delete barcode view.")
    if not validate_user():
        return returnPermissionError()
    return render_template('delete:barcode.html', USER=current_user, barcodes=database.get_all_barcodes())

@app.route('/delete/barcode/<string:uuid>')
@login_required
def delete_barcode(uuid):
    database.insert_history("PAGE_VISIT", current_user, "Viewed delete barcode.")
    if not validate_user():
        return returnPermissionError()
    database.delete_barcode(uuid)
    database.insert_history("DELETE", current_user, "Deleted barcode. UUID: " + str(uuid))
    return redirect('/delete/barcode')

@app.route('/delete/item/<string:uuid>')
@login_required
def delete_item(uuid):
    database.insert_history("PAGE_VISIT", current_user, "Viewed delete item.")
    if not validate_admin():
        return returnPermissionError()
    database.delete_item(uuid)
    database.insert_history("DELETE", current_user, "Deleted item. UUID: " + str(uuid))
    return redirect('/view')

@app.route('/delete/category')
@login_required
def delete_category_view():
    database.insert_history("PAGE_VISIT", current_user, "Viewed delete category view.")
    if not validate_admin():
        return returnPermissionError()
    return render_template('delete:category.html', USER=current_user, categories=database.get_deletable_categories())

@app.route('/delete/category/<string:uuid>')
@login_required
def delete_category(uuid):
    database.insert_history("PAGE_VISIT", current_user, "Viewed delete category.")
    if not validate_admin():
        return returnPermissionError()
    database.delete_category(uuid)
    database.insert_history("DELETE", current_user, "Deleted category. UUID: " + str(uuid))
    return redirect('/delete/category')

@app.route('/edit/item/<string:uuid>', methods=['GET', 'POST'])
@login_required
def edit_item(uuid):
    database.insert_history("PAGE_VISIT", current_user, "Viewed edit item.")
    if not validate_user():
        return returnPermissionError()

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

@app.route('/view/category/<string:uuid>')
def view_category(uuid):
    database.insert_history("PAGE_VISIT", current_user, "Viewed category " + str(uuid))
    return render_template('view:items.html', USER=current_user, category=database.get_category(uuid)['name'], items=database.get_all_items_for_category(uuid))

@app.route('/view/all')
def view_all_items():
    database.insert_history("PAGE_VISIT", current_user, "Viewed all items page")
    return render_template('view:items.html', USER=current_user, category='All items', items=database.get_all_items())

@app.route('/view/item/<string:uuid>')
def view_item(uuid):
    database.insert_history("PAGE_VISIT", current_user, "Viewed item " + str(uuid))
    return render_template('view:item.html', USER=current_user, item=database.get_item(uuid), barcodes=database.get_barcodes_for_item(uuid))

@app.route('/view')
def view():
    database.insert_history("PAGE_VISIT", current_user, "Viewed /view")
    return render_template('view.html', USER=current_user, categories=database.get_all_categories())

@app.route('/view/users')
@login_required
def view_users():
    database.insert_history("PAGE_VISIT", current_user, "Viewed users page")
    if not validate_admin():
        return returnPermissionError()
    return render_template('view:users.html', USER=current_user, users=database.get_all_users())

@app.route('/api/edit/user/<string:user_id>/<string:new_role>')
@login_required
def edit_user_role(user_id, new_role):
    database.insert_history("PAGE_VISIT", current_user, "Viewed edit user API")
    if not validate_admin():
        return returnPermissionError()
    print("Updating for:")
    print(str(base64.b64decode(user_id).decode('utf-8')))
    print(new_role)
    database.update_user_role(str(base64.b64decode(user_id).decode('utf-8')), new_role)
    database.insert_history("EDIT", current_user, "Edited user. UserId: " + str(user_id) + ", Role: " + str(new_role))
    return ""

@app.route('/barcode/check_in', methods=['GET', 'POST'])
@login_required
def barcode_check_in_item():
    database.insert_history("PAGE_VISIT", current_user, "Viewed barcode checkin")
    if not validate_user():
        return returnPermissionError()

    form_barcode = Barcode_Lookup(request.form)
    if request.method == 'POST' and form_barcode.validate():
        print(form_barcode.quantity.data)
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
    if not validate_user():
        return returnPermissionError()

    form_barcode = Barcode_Lookup(request.form)
    if request.method == 'POST' and form_barcode.validate():
        if database.scan_barcode_update_quantity(form_barcode.barcode.data, form_barcode.quantity.data):
            item_id = database.get_barcode(form_barcode.barcode.data)['item_id']
            database.insert_history("EDIT", current_user, "Check out with barcode. Barcode: " + str(form_barcode.barcode.data) + ", Quantity: " + str(form_barcode.quantity.data))
            return redirect('/view/item/' + item_id)
        else:
            flash("An error occurred when handling your request. Please validate the barcode and quantity.")

    return render_template('scan:barcode.html', USER=current_user, form=form_barcode, action="Check out", defaultQuantity=-1)

@app.route('/search/check_out', methods=['GET', 'POST'])
@login_required
def search_check_out_item():
    database.insert_history("PAGE_VISIT", current_user, "Viewed search checkout")
    if not validate_user():
        return returnPermissionError()
    
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
    if not validate_user():
        return returnPermissionError()
    
    form_search = Search_QuantityUpdate(request.form)

    if request.method == 'POST' and form_search.validate():
        if database.search_item_update_quantity(form_search.selectInput.data, form_search.quantity.data):
            database.insert_history("EDIT", current_user, "Check in with search. ItemId: " + str(form_search.selectInput.data) + ", Quantity: " + str(form_search.quantity.data))
            return redirect('/view/item/' + form_search.selectInput.data)
        else:
            flash("An error occurred when handling your request. Please validate the selection and quantity.")

    return render_template('search:updateqty.html', USER=current_user, form=form_search, action="Check in", defaultQuantity=1)

@app.route('/barcode/lookup', methods=['GET', 'POST'])
def barcode_look_up_item():
    database.insert_history("PAGE_VISIT", current_user, "Viewed barcode lookup")
    form_barcode = Barcode_Lookup(request.form)
    if request.method == 'POST' and form_barcode.validate():
        item_id = database.get_barcode(form_barcode.barcode.data)['item_id']
        database.insert_history("EDIT", current_user, "Barcode lookup. Barcode: " + str(form_barcode.barcode.data))
        return redirect('/view/item/' + item_id)

    return render_template('scan:barcode.html', USER=current_user, form=form_barcode, action="Look up")

@app.route('/view/history')
def view_history():
    database.insert_history("PAGE_VISIT", current_user, "Viewed history lookup")
    if not validate_admin():
        return returnPermissionError()

    return render_template('history.html', USER=current_user, events=database.get_history())
