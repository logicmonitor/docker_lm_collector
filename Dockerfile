FROM python:2.7

RUN pip install logicmonitor_core
RUN mkdir /usr/local/logicmonitor

# NTP is needed for some collector operations
RUN apt-get update && apt-get install -y ntp

COPY ./startup.py /startup.py

ENTRYPOINT ["python", "/startup.py"]
