import config

LOGGING_CONFIGURATION = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "default": {
            "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
        },
        "access": {
            "format": "%(message)s",
        }
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "default",
            "stream": "ext://sys.stdout",
        },
        "slack": {
            "class": "app.logging.slack_handler.SlackLoggingHandler",
            "formatter": "default",
            "level": "ERROR",
        },
        "db_application": {
            "class": "app.logging.db_handler.ApplicationLoggingHandler",
            "formatter": "default",
            "level": "INFO",
        },
        "db_access": {
            "class": "app.logging.db_handler.AccessLoggingHandler",
            "formatter": "default",
            "level": "INFO",
        },
        "error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "default",
            "filename": "/var/log/gunicorn.error.log",
            "maxBytes": 10000,
            "backupCount": 10,
            "delay": "True",
        },
        "access_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "access",
            "filename": "/var/log/gunicorn.access.log",
            "maxBytes": 10000,
            "backupCount": 10,
            "delay": "True",
        }
    },
    "loggers": {
        "gunicorn.error": {
            "handlers": ["console"] if config.DEBUG else ["slack", "error_file", "db_application"],
            "level": "INFO",
            "propagate": False,
        },
        "gunicorn.access": {
            "handlers": ["console"] if config.DEBUG else ["access_file", "db_access"],
            "level": "INFO",
            "propagate": False,
        }
    },
    "root": {
        "level": "DEBUG" if config.DEBUG else "INFO",
        "handlers": ["console"] if config.DEBUG else ["console", "slack", "db_application"],
    }
}
