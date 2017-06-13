FROM python:2.7-slim

RUN pip install logicmonitor_core
RUN mkdir /usr/local/logicmonitor

# NTP is needed for some collector operations
RUN apt-get update && apt-get install -y ntp

ADD https://static-prod.logicmonitor.com/logicmonitor-k8s/kubernetes.jar /tmp/kubernetes.jar
COPY ./startup.py /startup.py
COPY ./startup.sh /startup.sh
COPY ./shutdown.py /shutdown.py

ENTRYPOINT ["/startup.sh"]
