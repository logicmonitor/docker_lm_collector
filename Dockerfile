FROM python:3.10-slim

# NTP is needed for some collector operations
RUN apt-get update \
  && apt-get install --no-install-recommends -y \
  inetutils-traceroute \
  file \
  iputils-ping \
  ntp \
  perl \
  procps \
  xxd \
  && apt-get -y clean \
  && rm -rf /var/lib/apt/lists/*

RUN pip install logicmonitor_sdk==1.0.129
RUN mkdir /usr/local/logicmonitor

COPY collector /collector
COPY ./entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
