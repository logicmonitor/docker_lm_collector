#!/usr/bin/env bash

signal_handler() {
  echo $pid
  if [ ! -z $pid ]; then
    kill -s 15 $pid
    python /shutdown.py
    exit 0
  fi
}

# setup handlers
trap 'kill ${!}; signal_handler' SIGTERM
trap 'kill ${!}; signal_handler' SIGINT

# run application
python /startup.py &
pid="$!"

# wait forever
while true
do
  if [ -e "/usr/local/logicmonitor/agent/logs/wrapper.log" ]; then
    tail -f /usr/local/logicmonitor/agent/logs/wrapper.log & wait
  fi
done