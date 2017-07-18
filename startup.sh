#!/usr/bin/env bash

INSTALL_PATH=/usr/local/logicmonitor/agent
AGENT_BIN=$INSTALL_PATH/bin/logicmonitor-agent
PID_PATH=$INSTALL_PATH/bin/logicmonitor-agent.java.pid
LOG_PATH=$INSTALL_PATH/logs/wrapper.log
UNCLEAN_SHUTDOWN_PATH=$INSTALL_PATH/shutdown.lck

# setup handlers
trap 'signal_handler' SIGTERM
trap 'signal_handler' SIGINT

watch_pid() {
  # $1 = collector pid
  # $2 = pid of startup script
  while true
  do
    if ! $(ps -p $1 > /dev/null); then
      # we want cleanup scripts since the collector failed unexpectedly
      echo -e "Collector crashed\nExiting"
      touch $UNCLEAN_SHUTDOWN_PATH
      kill -INT $2
    fi
    sleep 10
  done
}

# catch shutdown signals from docker and run shutdown scripts
signal_handler() {
  # only cleanup if we shutdown cleanly
  if [ ! -f $UNCLEAN_SHUTDOWN_PATH ]; then
    /usr/local/logicmonitor/agent/bin/sbshutdown;
    python /collector/shutdown.py
    exit $?
  else
    rm $UNCLEAN_SHUTDOWN_PATH
    exit 1
  fi
}

set -e
# run application
python /collector/startup.py
# ensure the collector is stopped so that we can control startup
$AGENT_BIN stop > /dev/null
$AGENT_BIN start

# monitor the collector process and kill the container if it crashes
timeout 10 bash -c -- "\
  while [ ! -e $PID_PATH ]; do \
    echo 'Waiting for collector to start'; \
    sleep 1; \
  done"
echo "Collector started"
watch_pid $(cat $PID_PATH) $$ &

while true
do
  if [ -f $LOG_PATH ]; then
    tail -f $LOG_PATH & wait
  fi
done
