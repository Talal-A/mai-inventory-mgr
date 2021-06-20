import logging

from app.database import db_interface as database

# Emit application logs to db
class ApplicationLoggingHandler(logging.Handler):
    def __init__(self):
        super().__init__()

    def emit(self, record):
        try:
            if record.exc_info:  # for exceptions
                record.exc_text = logging._defaultFormatter.formatException(record.exc_info)
                record.exc_text = record.exc_text.replace("'",'"')         ## added for fixing quotes causing error 
            else:
                record.exc_text = ""
            database.insert_error_log(record)
        except:pass

# Emit access logs to db
class AccessLoggingHandler(logging.Handler):
    def __init__(self):
        super().__init__()

    def emit(self, record):
        try:
            if record.exc_info:  # for exceptions
                record.exc_text = logging._defaultFormatter.formatException(record.exc_info)
                record.exc_text = record.exc_text.replace("'",'"')         ## added for fixing quotes causing error 
            else:
                record.exc_text = ""
            database.insert_access_log(record)
        except:pass