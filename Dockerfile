FROM ubuntu:20.04
ENV DEBIAN_FRONTEND noninteractive

# NTP is needed for some collector operations
RUN apt update && apt-get update \
  && apt install software-properties-common -y \
  && add-apt-repository ppa:deadsnakes/ppa \
  && apt-get install --no-install-recommends -y \
  tcl \
  inetutils-traceroute \
  file \
  iputils-ping \
  ntp \
  perl \
  procps \
  xxd \
  python3.10 \
  python3-pip \
  && apt-get -y clean \
  && rm -rf /var/lib/apt/lists/* \
  && ln -s /usr/bin/python3.10 /usr/bin/python \
  && pip config set global.target /usr/local/lib/python3.10/dist-packages

RUN pip install logicmonitor_sdk==1.0.129
RUN mkdir /usr/local/logicmonitor

COPY collector /collector
COPY ./entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
