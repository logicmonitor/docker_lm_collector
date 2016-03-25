FROM python:2.7

RUN pip install logicmonitor_core
RUN mkdir /usr/local/logicmonitor

COPY ./startup.py /startup.py

CMD python /startup.py && \
    if [ $? -eq 0 ]; then \
        tail -f /usr/local/logicmonitor/agent/logs/wrapper.log; \
    fi
