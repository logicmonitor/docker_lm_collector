#!/bin/bash
python /startup.py
tail -f /usr/local/logicmonitor/agent/logs/wrapper.log
