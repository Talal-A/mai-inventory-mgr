# run.py

from app import app, database
import sys

if __name__ == '__main__':
    database.__init_db()
    if len(sys.argv) == 2 and sys.argv[1] is "d":
        app.run(host='0.0.0.0', port=9205, ssl_context="adhoc")
    else:
        app.run(host='0.0.0.0', port=9205)