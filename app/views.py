# views.py

from flask import render_template, request, redirect, flash
from wtforms import Form, StringField, validators, ValidationError, SubmitField, TextAreaField

from app import app
from .db import insertCategory, getCategories, getCategoryForId, updateCategory, insertItem, getItems, getItemForId, updateItem, getDeletableCategories, deleteCategory, insertBarcode, getBarcodesForItem, getBarcodes, deleteBarcode, getItemsForCategory, deleteItem, getBarcode, scanBarcodeAndUpdateQuantity
from .register import Register_Category, Register_Item, Update_Item, Register_Barcode, Barcode_Lookup
import requests

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

USERNAME="Talal"

# WIP AUTH
GOOGLE_CLIENT_ID = os.environ.get("MAI_GOOGLE_CLIENT_ID", None)
GOOGLE_CLIENT_SECRET = os.environ.get("MAI_GOOGLE_CLIENT_SECRET", None)
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()


client = WebApplicationClient(GOOGLE_CLIENT_ID)


# END WIP AUTH

@app.route('/')
def index():
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
    else:
        return "User email not available or not verified by Google.", 400

    return redirect('/dashboard')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/dashboard')

@app.route('/dashboard')
def dashboard():
    print(str(current_user.is_authenticated))
    print(current_user.name)
    print(current_user.role)
    return render_template('dashboard.html', USER=USERNAME)

@app.route('/feedback')
def feedback():
    return render_template('feedback.html', USER=USERNAME)

@app.route('/register/<string:type>', methods=['GET', 'POST'])
def register_with_param(type):
    form_category = Register_Category(request.form)
    form_item = Register_Item(request.form)
    form_barcode = Register_Barcode(request.form)

    if type == 'category':
        if request.method == 'POST' and form_category.category.data and form_category.validate():
            insertCategory(form_category.category.data)
            return redirect('/dashboard')

        return render_template('register:' + type + '.html', USER=USERNAME, form=form_category)

    elif type == 'item':
        if request.method == 'POST' and form_item.category.data and form_item.item.data and form_item.validate():
            insertItem(str(form_item.category.data).strip(), str(form_item.item.data).strip(), str(form_item.location.data).strip())
            return redirect('/dashboard')

        return render_template('register:' + type + '.html', USER=USERNAME, form=form_item, categories=getCategories())

    elif type == 'barcode':
        if request.method == 'POST' and form_barcode.validate():
            insertBarcode(str(form_barcode.barcode.data).strip(), str(form_barcode.item.data).strip())
            return redirect('/dashboard')

        return render_template('register:' + type + '.html', USER=USERNAME, form=form_barcode, categories=getCategories())

    else:
        return redirect('/dashboard')

@app.route('/edit/item/add_barcode/<string:uuid>', methods=['GET', 'POST'])
def register_barcode_for_item(uuid):
    form_barcode = Register_Barcode(request.form)
    form_barcode.item.data = str(uuid)
    form_barcode.item.render_kw = {'disabled':'disabled'}

    print(form_barcode.item.data)
    if request.method == 'POST' and form_barcode.validate():
        insertBarcode(str(form_barcode.barcode.data).strip(), str(form_barcode.item.data).strip())
        return redirect('/view/item/' + uuid)

    return render_template('register:' + 'barcode' + '.html', USER=USERNAME, form=form_barcode)

@app.route('/edit/category/<string:uuid>', methods=['GET', 'POST'])
def edit_category(uuid):
    form_category = Register_Category(request.form)

    if request.method == 'POST' and form_category.category.data and form_category.validate():
        updateCategory(uuid, form_category.category.data)
        return redirect('/view')
    else:
        form_category.category.data = getCategoryForId(uuid)['name']

    return render_template('edit:category.html', USER=USERNAME, form=form_category)

@app.route('/delete/barcode')
def delete_barcode_view():
    return render_template('delete:barcode.html', USER=USERNAME, barcodes=getBarcodes())

@app.route('/delete/barcode/<string:uuid>')
def delete_barcode(uuid):
    deleteBarcode(uuid)
    return redirect('/delete/barcode')

@app.route('/delete/item/<string:uuid>')
def delete_item(uuid):
    deleteItem(uuid)
    return redirect('/view')

@app.route('/delete/category')
def delete_category_view():
    return render_template('delete:category.html', USER=USERNAME, categories=getDeletableCategories())

@app.route('/delete/category/<string:uuid>')
def delete_category(uuid):
    deleteCategory(uuid)
    return redirect('/delete/category')

@app.route('/edit/item/<string:uuid>', methods=['GET', 'POST'])
def edit_item(uuid):
    form_item = Update_Item(request.form)

    if request.method == 'POST' and form_item.validate():
        updateItem(uuid, form_item.category.data, form_item.location.data, form_item.quantity_active.data, form_item.quantity_expired.data, form_item.notes.data, form_item.url.data)
        return redirect('/view/item/' + uuid)
    else:
        current_item = getItemForId(uuid)
        form_item.category.data = current_item['category_id']
        form_item.location.data = current_item['location']
        form_item.quantity_active.data = current_item['quantity_active']
        form_item.quantity_expired.data = current_item['quantity_expired']
        form_item.notes.data = current_item['notes']
        form_item.url.data = current_item['url']

    return render_template('edit:item.html', USER=USERNAME, form=form_item, item_name=current_item['name'])

@app.route('/view/category/<string:uuid>')
def view_category(uuid):
    return render_template('view:items.html', USER=USERNAME, category=getCategoryForId(uuid)['name'], items=getItemsForCategory(uuid))

@app.route('/view/all')
def view_all_items():
    return render_template('view:items.html', USER=USERNAME, category='All items', items=getItems())

@app.route('/view/item/<string:uuid>')
def view_item(uuid):
    return render_template('view:item.html', USER=USERNAME, item=getItemForId(uuid), barcodes=getBarcodesForItem(uuid))

@app.route('/view')
def view():
    return render_template('view.html', USER=USERNAME, categories=getCategories())

@app.route('/barcode/check_in', methods=['GET', 'POST'])
def barcode_check_in_item():
    form_barcode = Barcode_Lookup(request.form)
    if request.method == 'POST' and form_barcode.validate():
        print("okay...")
        print(form_barcode.quantity.data)
        if scanBarcodeAndUpdateQuantity(form_barcode.barcode.data, form_barcode.quantity.data):
            item_id = getBarcode(form_barcode.barcode.data)['item_id']
            return redirect('/view/item/' + item_id)
        else:
            flash("An error occurred when handling your request. Please validate the barcode and quantity.")

    return render_template('scan:barcode.html', USER=USERNAME, form=form_barcode, action="Check in", defaultQuantity=1)

@app.route('/barcode/check_out', methods=['GET', 'POST'])
def barcode_check_out_item():
    form_barcode = Barcode_Lookup(request.form)
    if request.method == 'POST' and form_barcode.validate():
        if scanBarcodeAndUpdateQuantity(form_barcode.barcode.data, form_barcode.quantity.data):
            item_id = getBarcode(form_barcode.barcode.data)['item_id']
            return redirect('/view/item/' + item_id)
        else:
            flash("An error occurred when handling your request. Please validate the barcode and quantity.")

    return render_template('scan:barcode.html', USER=USERNAME, form=form_barcode, action="Check out", defaultQuantity=-1)

@app.route('/barcode/lookup', methods=['GET', 'POST'])
def barcode_look_up_item():
    form_barcode = Barcode_Lookup(request.form)
    if request.method == 'POST' and form_barcode.validate():
        item_id = getBarcode(form_barcode.barcode.data)['item_id']
        return redirect('/view/item/' + item_id)

    return render_template('scan:barcode.html', USER=USERNAME, form=form_barcode, action="Look up")
