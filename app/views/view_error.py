from app import app
from flask_login import current_user
from flask import redirect, render_template, request

@app.errorhandler(Exception)
def redirect_error(e):
    app.logger.error("An error occurred at %s", request.url, exc_info=True)
    return redirect('/error')

@app.route('/error')
def error():
    return render_template('view:error.html', USER=current_user)