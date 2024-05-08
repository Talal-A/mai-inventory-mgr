import os

# Enable Flask's debugging features. Should be False in production
DEBUG = False

# Google authentication 
GOOGLE_CLIENT_ID = os.environ.get("MAI_GOOGLE_CLIENT_ID", None)
GOOGLE_CLIENT_SECRET = os.environ.get("MAI_GOOGLE_CLIENT_SECRET", None)
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

# Imgur variables
IMGUR_CLIENT_ID = os.environ.get("MAI_IMGUR_CLIENT_ID", None)

# Slack error logging url
SLACK_LOGGING_URL = os.environ.get("SLACK_LOGGING_URL", None)

# Stage
STAGE = os.environ.get("STAGE", "dev")