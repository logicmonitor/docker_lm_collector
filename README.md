# lm_collector

## Overview
Docker image capable of installing and running a LogicMonitor collector

## Requirements
You must have a LogicMonitor account

## Usage
This container will utilize environment variables to authenticate to your
LogicMonitor portal.

company - your company's name

username - your LogicMonitor username

password - your LogicMonitor password

## Example
```
docker run --name lm_collector -d \
-e company=<your-company> \
-e username=<your-username> \
-e password=<your-password> \
logicmonitor/lm_collector:latest
```
