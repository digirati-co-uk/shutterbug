# Shutterbug

Automate creation of ElasticSearch snapshots in an S3 repository.

[![Build Status](https://travis-ci.org/fractos/shutterbug.svg?branch=master)](https://travis-ci.org/fractos/shutterbug)

## Table of Contents
<!-- TOC orderedList:false -->

- [Shutterbug](#shutterbug)
  - [Table of Contents](#table-of-contents)
  - [Environment variables](#environment-variables)
  - [REPOSITORY_SETTINGS](#repository_settings)
- [Usage](#usage)

<!-- /TOC -->

## Environment variables

| Name                     | Description                                                   | Default                                              |
|--------------------------|---------------------------------------------------------------|------------------------------------------------------|
| DEBUG                    | Whether to produce debug messages in the log                  | False                                                |
| ES_HOST                  | Full URL for the ElasticSearch instance                       | http://elasticsearch:9200                            |
| REPOSITORY_NAME          | Name of the repository to use and create if not present       | s3                                                   |
| REMOVE_OLDER_THAN_DAYS   | Number of days of snapshots to keep (0 to disable)            | 0                                                    |
| SLACK_WEBHOOK_URL        | Webhook URL                                                   | http://slack/webhook/url                             |
| ENABLE_SLACK             | Whether to use the SLACK_WEBHOOK_URL to emit message          | False                                                |
| REPOSITORY_SETTINGS      | JSON blob for `repository-s3` settings                        | {"type": "s3", "settings": {"bucket":"bucket-name"}} |
| INDEX_NAMES              | List of comma-separated index names to snapshot (empty = all) |                                                      |
| IGNORE_UNAVAILABLE       | `ignore_unavailable` parameter for snapshot                   | False                                                |
| SNAPSHOT_PREFIX          | Snapshots will be named with this prefix                      |                                                      |
| INCLUDE_GLOBAL_STATE     | `include_global_state` parameter for snapshot                 | True                                                 |
| REQUEST_TIMEOUT_SECONDS  | Timeout value for general ES requests                         | 30                                                   |
| SNAPSHOT_TIMEOUT_SECONDS | Timeout value for ES snapshot requests (0 to disable)         | 60                                                   |
| SLACK_MESSAGE_PREFIX     | Slack messages will receive this prefix                       | "shutterbug: "                                       |
| ANNOUNCE_SUCCESS         | If `False`, only failure/error messages announced to Slack    | True                                                 |

## REPOSITORY_SETTINGS

Documentation of settings can be found here: https://www.elastic.co/guide/en/elasticsearch/plugins/current/repository-s3-repository.html

The REPOSITORY_SETTINGS value is the JSON blob that is used when creating the snapshot repository.

# Usage

```
docker run -t -i --rm --name shutterbug \
  --env ES_HOST='http://elasticsearch.local:9200' \
  --env REPOSITORY_NAME='my_s3_repository' \
  --env REMOVE_OLDER_THAN_DAYS='30' \
  --env SLACK_WEBHOOK_URL='https://slack.com/webhooks/id/token' \
  --env ENABLE_SLACK='True' \
  --env REPOSITORY_SETTINGS='{"type": "s3", "settings": {"bucket":"my-s3-bucket", "base_path": "my/backup/prefix", "storage_class": "standard_ia"}}' \
  fractos/shutterbug
```
This will attempt to create the snapshot repository if it doesn't already exist using a command similar to:
```
PUT _snapshot/my_s3_repository
{
  "type": "s3",
  "settings": {
    "bucket": "my-s3-bucket",
    "base_path":"my/backup/prefix",
    "storage_class": "standard_ia"
  }
}
```
