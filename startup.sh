#!/usr/bin/env bash

INSTALL_PATH=/usr/local/logicmonitor/agent
AGENT_BIN=$INSTALL_PATH/bin/logicmonitor-agent
AGENT_PID_PATH=$INSTALL_PATH/bin/logicmonitor-agent.java.pid
WATCHDOG_BIN=$INSTALL_PATH/bin/logicmonitor-watchdog
WATCHDOG_PID_PATH=$INSTALL_PATH/bin/logicmonitor-watchdog.java.pid
LOG_PATH=$INSTALL_PATH/logs/wrapper.log
UNCLEAN_SHUTDOWN_PATH=$INSTALL_PATH/unclean_shutdown.lck

# setup handlers
trap 'signal_handler' SIGTERM
trap 'signal_handler' SIGINT

watch_pid() {
  # $1 = collector pid
  # $2 = pid of startup script
  while true
  do
    if ! $(ps -p $1 > /dev/null); then
      # we want to skip cleanup scripts since the collector failed unexpectedly
      echo -e "Watchdog crashed\nExiting"
      touch $UNCLEAN_SHUTDOWN_PATH
      kill -INT $2
    fi
    sleep 10
  done
}

watch_agent() {
  # $1 = pid of startup script

  # check if the agent is running, and if not, make a note
  FAIL=0
  while true
  do
    timeout 10 bash -c -- "\
      while [ ! -e $AGENT_PID_PATH ]; do \
        echo 'Waiting for agent to start'; \
        sleep 1; \
      done"

    # make sure the PID file exists
    if [ -e $AGENT_PID_PATH ]; then
      # get the current PID of the collector agent
      AGENT_PID=$(cat $AGENT_PID_PATH)
    fi

    # if we failed to grab a PID, increment failures and try again
    if [ -z "$AGENT_PID" ]; then
      FAIL=$(($FAIL+1))
      sleep 10
      continue
    fi

    if ! $(ps -p $AGENT_PID > /dev/null); then
      FAIL=$(($FAIL+1))
    else
      FAIL=0
    fi

    # if the agent has been down for 6 iterations (1m), it's time to fail
    if [ "$FAIL" -ge 6 ]; then
      # we want to skip cleanup scripts since the collector failed unexpectedly
      echo -e "Agent crashed\nExiting"
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
$WATCHDOG_BIN stop > /dev/null
$WATCHDOG_BIN start

# monitor the watchdog process and kill the container if it crashes
timeout 10 bash -c -- "\
  while [ ! -e $WATCHDOG_PID_PATH ]; do \
    echo 'Waiting for watchdog to start'; \
    sleep 1; \
  done"
echo "Watchdog started"
watch_pid $(cat $WATCHDOG_PID_PATH) $$ &

# monitor the agent process and kill the container if it is down for 60s
watch_agent $$ &

while true
do
  if [ -f $LOG_PATH ]; then
    tail -f $LOG_PATH & wait
  fi
done
