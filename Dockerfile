FROM python:2.7-slim

# NTP is needed for some collector operations
RUN apt-get update \
  && apt-get install --no-install-recommends -y \
  ntp \
  perl \
  procps \
  && apt-get -y clean \
  && rm -rf /var/lib/apt/lists/*

RUN pip install logicmonitor_sdk
RUN mkdir /usr/local/logicmonitor

ADD collector /collector
COPY ./entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
