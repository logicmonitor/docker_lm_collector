# lm_collector

## Overview
Docker image capable of installing and running a LogicMonitor collector

#### Note that this is beta functionality, and as such LogicMonitor support will not be able to assist in any issues that arise.  Instead, please create issues directly in this GitHub repository.

## Website
http://www.logicmonitor.com

## Docker repository
https://hub.docker.com/r/logicmonitor/lm_collector/

## Requirements
You must have a LogicMonitor account

## Usage
This container will utilize environment variables to authenticate to your
LogicMonitor portal.

company - your company's name

username - your LogicMonitor username

password - your LogicMonitor password

collector_id - OPTIONAL. The id of an existing LogicMonitor collector. The
container will start up as the specified collector. Cannot be used with
the cleanup option.

cleanup - if this is non-null, the collector will remove itself from the portal
when the container is stopped.

## Example
```
docker run --name lm_collector -d \
    -e company=<your-company> \
    -e username=<your-username> \
    -e password=<your-password> \
    -e collector_id=<existing collector id> \
    -e cleanup=true \
logicmonitor/lm_collector:latest
```
