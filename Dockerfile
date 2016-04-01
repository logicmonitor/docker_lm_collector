FROM python:2.7

RUN pip install logicmonitor_core
RUN mkdir /usr/local/logicmonitor

# NTP is needed for some collector operations
RUN apt-get update && apt-get install -y ntp

COPY ./startup.py /startup.py

CMD python /startup.py && \
    if [ $? -eq 0 ]; then \
        tail -f /usr/local/logicmonitor/agent/logs/wrapper.log; \
    fi
