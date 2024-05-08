import config
from multiprocessing import Queue

LOGGING_CONFIGURATION = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "default": {
            "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
        },
        "loki": {
            "format": "%(levelname)s in %(module)s: %(message)s",
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
        "loki": {
            "class": "logging_loki.LokiQueueHandler",
            "queue": Queue(-1),
            "url": "https://loki.abouhaiba.com/loki/api/v1/push",
            "tags": {"application": "mai-inventory-mgr", "stage": config.STAGE},
            "formatter": "loki",
            "version": "1",
        },
    },
    "loggers": {
        "gunicorn.error": {
            "handlers": ["console", "loki"] if config.DEBUG else ["loki"],
            "level": "INFO",
            "propagate": False,
        },
        "gunicorn.access": {
            "handlers": ["console", "loki"] if config.DEBUG else ["loki"],
            "level": "INFO",
            "propagate": False,
        }
    },
    "root": {
        "level": "DEBUG" if config.DEBUG else "INFO",
        "handlers": ["console", "loki"] if config.DEBUG else ["loki"]
    }
}
