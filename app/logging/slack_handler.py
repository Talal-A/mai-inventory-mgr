import json
import requests
import logging
import config

# Emit ERROR logs to slack
class SlackLoggingHandler(logging.Handler):
    def __init__(self):
        super().__init__()

    def emit(self, record):
        log_entry = self.format(record)
        json_text = json.dumps({"text": log_entry})
        requests.post(config.SLACK_LOGGING_URL, json_text, headers={"Content-type": "application/json"})
