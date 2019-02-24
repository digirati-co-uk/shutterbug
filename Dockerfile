FROM alpine:3.6

RUN apk add --update --no-cache --virtual=run-deps \
  python3 \
  ca-certificates \
  && rm -rf /var/cache/apk/*

ENV ES_HOST http://elasticsearch:9200
ENV REPOSITORY_NAME s3
ENV REMOVE_OLDER_THAN_DAYS 0
ENV SLACK_WEBHOOK_URL http://slack/webhook/url
ENV ENABLE_SLACK False
ENV REPOSITORY_SETTINGS {"type": "s3", "settings": {"bucket": "bucket-name"}}
ENV SNAPSHOT_PREFIX ""
ENV IGNORE_UNAVAILABLE False
ENV INCLUDE_GLOBAL_STATE True
ENV REQUEST_TIMEOUT_SECONDS 30
ENV SNAPSHOT_TIMEOUT_SECONDS 60
ENV SLACK_MESSAGE_PREFIX "shutterbug: "

WORKDIR /opt/app
CMD ["python3", "-u", "shutterbug.py"]

COPY requirements.txt /opt/app/
RUN pip3 install --no-cache-dir -r /opt/app/requirements.txt

COPY app /opt/app/
