import os
import distutils.util

DEBUG = bool(distutils.util.strtobool(os.getenv("DEBUG", default="False")))
ES_HOST = os.getenv("ES_HOST")
REPOSITORY_NAME = os.getenv("REPOSITORY_NAME")
REMOVE_OLDER_THAN_DAYS = int(os.getenv("REMOVE_OLDER_THAN_DAYS"))
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
ENABLE_SLACK = bool(distutils.util.strtobool(os.getenv("ENABLE_SLACK")))
REPOSITORY_SETTINGS = os.getenv("REPOSITORY_SETTINGS")
INDEX_NAMES = os.getenv("INDEX_NAMES")
IGNORE_UNAVAILABLE = bool(distutils.util.strtobool(os.getenv("IGNORE_UNAVAILABLE", default="False")))
INCLUDE_GLOBAL_STATE = bool(distutils.util.strtobool(os.getenv("INCLUDE_GLOBAL_STATE", default="True")))
REQUEST_TIMEOUT_SECONDS = int(os.getenv("REQUEST_TIMEOUT_SECONDS", default="30"))
SNAPSHOT_TIMEOUT_SECONDS = int(os.getenv("SNAPSHOT_TIMEOUT_SECONDS", default="60"))
SLACK_MESSAGE_PREFIX = os.getenv("SLACK_MESSAGE_PREFIX", default="shutterbug: ")