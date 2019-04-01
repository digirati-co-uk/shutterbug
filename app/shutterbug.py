import logging
from logzero import logger
import logzero
from urllib.parse import urlparse
from datetime import datetime, timezone, date
from dateutil.relativedelta import relativedelta
import dateutil.parser
from concurrent.futures.thread import ThreadPoolExecutor
import re
import socket
import http.client
import json
import time
import requests
import os
import settings


def main():
    logger.info("starting...")

    try:
        if not repository_exists():
            if not create_repository():
                raise Exception("couldn't create repository")

        if settings.REMOVE_OLDER_THAN_DAYS > 0:
            remove_old_snapshots()

        if not create_snapshot():
            raise Exception("couldn't create snapshot")

    except Exception as e:
        logger.fatal(str(e))
        if settings.ENABLE_SLACK:
            slack_announce(message=str(e))


def repository_exists():
    logger.info(f"checking if repository {settings.REPOSITORY_NAME} exists")
    r = None
    try:
        r = requests.get(
            url=f"{settings.ES_HOST}/_snapshot/{settings.REPOSITORY_NAME}",
            timeout=settings.REQUEST_TIMEOUT_SECONDS
        )
    except Exception as e:
        logger.fatal(f"problem while contacting {settings.ES_HOST}: {str(e)}")
        raise

    logger.debug(f"response: {r} {r.text}")

    return r.status_code != 404


def create_repository():
    logger.info(f"creating repository {settings.REPOSITORY_NAME}")

    r = None
    try:
        url = f"{settings.ES_HOST}/_snapshot/{settings.REPOSITORY_NAME}"

        logger.debug(f"request: url={url} data={settings.REPOSITORY_SETTINGS} timeout={settings.REQUEST_TIMEOUT_SECONDS}")

        r = requests.put(
            url=url,
            data=settings.REPOSITORY_SETTINGS,
            timeout=settings.REQUEST_TIMEOUT_SECONDS
        )

    except Exception as e:
        logger.fatal(f"problem while creating repository on {settings.ES_HOST}: {str(e)}")
        raise

    logger.debug(f"response: {r} {r.text}")

    if r.status_code == 200:
        announce(f"repository {settings.REPOSITORY_NAME} created")
    else:
        announce(f"repository {settings.REPOSITORY_NAME} not created! reason: {r} {r.text}")

    return r.status_code == 200


def create_snapshot():
    timestamp = datetime.utcfromtimestamp(time.time()).strftime('%Y%m%d%H%M%S')
    snapshot_name = f"{settings.SNAPSHOT_PREFIX}{timestamp}"
    logger.info(f"creating snapshot {snapshot_name} in {settings.REPOSITORY_NAME}")

    wait_for_completion = (settings.SNAPSHOT_TIMEOUT_SECONDS != 0)

    timeout = settings.SNAPSHOT_TIMEOUT_SECONDS

    if wait_for_completion:
        logger.info(f"shutterbug will wait {settings.SNAPSHOT_TIMEOUT_SECONDS} second(s) maximum")
    else:
        logger.info(f"shutterbug will not wait for snapshot to be complete")
        timeout = settings.REQUEST_TIMEOUT_SECONDS

    json = {
        "ignore_unavailable": settings.IGNORE_UNAVAILABLE,
        "include_global_state": settings.INCLUDE_GLOBAL_STATE
    }

    if settings.INDEX_NAMES is None or len(settings.INDEX_NAMES) == 0:
        logger.info(f"all indices will be included")
    else:
        logger.info(f"only these indices will be included: {settings.INDEX_NAMES}")
        json["index_names"] = settings.INDEX_NAMES

    r = None
    try:
        url = f"{settings.ES_HOST}/_snapshot/{settings.REPOSITORY_NAME}/{snapshot_name}?wait_for_completion={str(wait_for_completion).lower()}"

        logger.debug(f"request: url={url} data={json} timeout={timeout}")

        r = requests.put(
            url=url,
            json=json,
            timeout=timeout
        )
    except Exception as e:
        logger.fatal(f"problem while creating snapshot {snapshot_name} on {settings.ES_HOST}: {str(e)}")
        raise

    logger.debug(f"response: {r} {r.text}")

    if r.status_code == 200:
        if wait_for_completion:
            announce(f"snapshot {snapshot_name} created")
        else:
            announce(f"snapshot {snapshot_name} accepted")
    else:
        announce(f"snapshot {snapshot_name} not created! reason: {r} {r.text}")

    return r.status_code == 200


def announce(message):
    logger.info(message)
    if settings.ENABLE_SLACK:
        slack_announce(message)


def slack_announce(message):
    posted_message = f"{settings.SLACK_MESSAGE_PREFIX}{message}"
    logger.debug(f"slack_announce({settings.SLACK_WEBHOOK_URL}, {posted_message}")
    _ = requests.post(settings.SLACK_WEBHOOK_URL, json={"text": posted_message, "link_names": 1})


def remove_old_snapshots():
    logger.debug(f"remove_old_snapshots()")

    # get list of repository snapshots
    r = None

    try:
        url = f"{settings.ES_HOST}/_snapshot/{settings.REPOSITORY_NAME}/_all"

        logger.debug(f"request: {url}")

        r = requests.get(
            url=url,
            timeout=settings.REQUEST_TIMEOUT_SECONDS
        )

    except Exception as e:
        logger.fatal(f"problem while getting list of snapshots: {str(e)}")
        raise

    logger.debug(f"response: {r} {r.text}")

    snapshots = r.json()

    if "snapshots" not in snapshots:
        logger.fatal(f"couldn't find 'snapshots' property in response: {r} {r.text}")
        raise Exception(f"problem parsing reply from list of snapshots: {r} {r.text}")

    for snapshot in snapshots["snapshots"]:
        start_time = snapshot["start_time"]
        snapshot_name = snapshot["snapshot"]

        # start_time is in Zulu time - e.g. "start_time": "2019-02-23T19:39:28.043Z"
        # this is ISO-8601 compliant
        snapshot_date = dateutil.parser.parse(start_time)
        delta = datetime.now(timezone.utc) - snapshot_date

        if settings.REMOVE_OLDER_THAN_DAYS > 0 and delta.days > settings.REMOVE_OLDER_THAN_DAYS:
            logger.info(f"snapshot {snapshot_name} is a candidate for removal")
            if remove_snapshot(snapshot_name):
                logger.info(f"snapshot {snapshot_name} has been removed")
            else:
                raise Exception(f"snapshot removal failed")


def remove_snapshot(snapshot_name):
    logger.info(f"remove_snapshot {snapshot_name}")

    r = None
    try:
        url = f"{settings.ES_HOST}/_snapshot/{settings.REPOSITORY_NAME}/{snapshot_name}"
        r = requests.delete(url, timeout=settings.REQUEST_TIMEOUT_SECONDS)
    except Exception as e:
        logger.fatal(f"problem during removal of snapshot {snapshot_name}: {str(e)}")
        raise

    logger.debug(f"response: {r} {r.text}")

    return r.status_code == 200



if __name__ == "__main__":
    if settings.DEBUG:
        logzero.loglevel(logging.DEBUG)
    else:
        logzero.loglevel(logging.INFO)

    main()
