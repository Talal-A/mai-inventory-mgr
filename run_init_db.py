# run_init_db.py
# To be called before starting gunicorn, used to make sure that
# only one process instantiates and upgrades the database.

from app.database import db_interface as database

if __name__ == '__main__':
    database.init_db()