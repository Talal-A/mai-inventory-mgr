# run.py

from app import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9205, ssl_context="adhoc")
