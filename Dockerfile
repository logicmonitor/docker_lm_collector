FROM python:2.7-slim

# NTP is needed for some collector operations
RUN apt-get update \
&& apt-get install --no-install-recommends -y \
  ntp \
  perl \
&& apt-get -y clean \
&& rm -rf /var/lib/apt/lists/*

RUN pip install logicmonitor_sdk==0.0.1.4
RUN mkdir /usr/local/logicmonitor

COPY collector /collector
COPY ./startup.sh /startup.sh

ENTRYPOINT ["/startup.sh"]
