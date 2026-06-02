from app import app
from flask_login import current_user, login_required
from flask import request, jsonify

from app.database import db_interface as database
from app.register import Register_Category
from app.views import view_util

import base64

@app.route('/api/edit/user/<string:user_id>/<string:new_role>')
@login_required
def edit_user_role(user_id, new_role):
    if not view_util.validate_admin():
        return view_util.returnPermissionError()
    database.update_user_role(str(base64.b64decode(user_id).decode('utf-8')), new_role)
    return ""

@app.route('/api/item/<string:item_id>/images')
def api_item_images(item_id):
    images = database.get_all_images_for_item(item_id)
    return jsonify({'images': [img['image_url'] for img in images]})

@app.route('/api/browse')
def api_browse():
    search = request.args.get('search', '').strip()
    category_id = request.args.get('category', '').strip()
    subcategory_id = request.args.get('subcategory', '').strip()
    allowed_sort_by = {'name', 'category', 'quantity'}
    allowed_sort_order = {'asc', 'desc'}

    raw_sort_by = request.args.get('sort_by', 'name')
    sort_by = raw_sort_by if raw_sort_by in allowed_sort_by else 'name'

    raw_sort_order = request.args.get('sort_order', 'asc').lower()
    sort_order = raw_sort_order if raw_sort_order in allowed_sort_order else 'asc'
    hide_out_of_stock = request.args.get('hide_out_of_stock', '0') == '1'

    try:
        page = int(request.args.get('page', 0))
        page = max(0, page)
    except (ValueError, TypeError):
        page = 0

    try:
        page_size = int(request.args.get('page_size', 24))
        page_size = max(1, min(page_size, 100))
    except (ValueError, TypeError):
        page_size = 24

    items, total_count = database.browse_items(
        search=search,
        category_id=category_id,
        subcategory_id=subcategory_id,
        sort_by=sort_by,
        sort_order=sort_order,
        hide_out_of_stock=hide_out_of_stock,
        offset=page * page_size,
        limit=page_size
    )

    return jsonify({
        'items': items,
        'total_count': total_count,
        'page': page,
        'page_size': page_size,
        'has_more': (page + 1) * page_size < total_count
    })
