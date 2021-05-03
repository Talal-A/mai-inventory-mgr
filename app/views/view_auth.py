from app import app
from flask import request, redirect
from oauthlib.oauth2 import WebApplicationClient

from app.user import User
from app.database import db_interface as database

from flask_login import login_user, current_user, logout_user, login_required

import requests
import config
import json

auth_client = WebApplicationClient(config.GOOGLE_CLIENT_ID)

def __get_google_provider_cfg():
    return requests.get(config.GOOGLE_DISCOVERY_URL).json()

@app.route('/login')
def login():
    # Find out what URL to hit for Google login
    google_provider_cfg = __get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = auth_client.prepare_request_uri(
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
    google_provider_cfg = __get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send a request to get tokens! Yay tokens!
    token_url, headers, body = auth_client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(config.GOOGLE_CLIENT_ID, config.GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    auth_client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that you have tokens (yay) let's find and hit the URL
    # from Google that gives you the user's profile information,
    # including their Google profile image and email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = auth_client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # You want to make sure their email is verified.
    # The user authenticated with Google, authorized your
    # app, and now you've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        users_name = userinfo_response.json()["given_name"]
        users_picture = userinfo_response.json()["picture"]

        user = None

        if not database.exists_user_id(unique_id):
            User.create(unique_id, users_name, users_email, 0, users_picture)
            user = User(id_=unique_id, name=users_name, email=users_email, role=0, picture=users_picture)
        else:
            # Returning user, refresh their data first
            database.update_user_info(unique_id, users_name, users_email, users_picture)
            user = User.get(unique_id)

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
