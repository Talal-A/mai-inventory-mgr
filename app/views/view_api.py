from app import app
from flask_login import current_user, login_required
from flask import request

from app.database import db_interface as database
from app.register import Register_Category, Register_Barcode, Register_Item
from app.views import view_util

import base64

@app.route('/api/edit/user/<string:user_id>/<string:new_role>')
@login_required
def edit_user_role(user_id, new_role):
    if not view_util.validate_admin():
        return view_util.returnPermissionError()
    database.update_user_role(str(base64.b64decode(user_id).decode('utf-8')), new_role)
    return ""
