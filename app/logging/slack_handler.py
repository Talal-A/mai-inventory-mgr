import json
import requests
import logging
import config

# Emit ERROR logs to slack
class SlackLoggingHandler(logging.Handler):
    def __init__(self):
        print("Hello world from beginning of slcak handler")
        super().__init__()

    def emit(self, record):
        print("Hello world from slack handler")
        log_entry = self.format(record)
        json_text = json.dumps({"text": log_entry})
        requests.post(config.SLACK_LOGGING_URL, json_text, headers={"Content-type": "application/json"})
