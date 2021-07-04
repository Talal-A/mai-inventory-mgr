from . import db_util as db
from datetime import datetime

def insert_error_log(record):
    db_connection = db.__get_log_db()
    cursor = db_connection.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO error_log (date, source, log_level, log_level_name, message, args, 
            module, function_name, line_num, exception, process, thread, thread_name)
        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (
            int(record.created), 
            str(record.name),
            int(record.levelno),
            str(record.levelname),
            str(record.message),
            str(record.args),
            str(record.module),
            str(record.funcName),
            int(record.lineno),
            str(record.exc_text),
            int(record.process),
            str(record.thread),
            str(record.threadName)
        ))

    db_connection.commit()
    cursor.close()

def insert_access_log(record):
    db_connection = db.__get_log_db()
    cursor = db_connection.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO access_log (date, source, log_level, log_level_name, message, args, 
            module, function_name, line_num, exception, process, thread, thread_name)
        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (
            int(record.created), 
            str(record.name),
            int(record.levelno),
            str(record.levelname),
            str(record.message),
            str(record.args),
            str(record.module),
            str(record.funcName),
            int(record.lineno),
            str(record.exc_text),
            int(record.process),
            str(record.thread),
            str(record.threadName)
        ))

    db_connection.commit()
    cursor.close()

def insert_latency_log(path, time):
    db_connection = db.__get_log_db()
    cursor = db_connection.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO latency_log (date, path, time)
        VALUES(?, ?, ?)""", (
            datetime.now().timestamp(),
            str(path),
            int(time)
        ))

    db_connection.commit()
    cursor.close()