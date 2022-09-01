> :warning: **Archived**: We are no more maintainig this codebase. See docker images on docker hub or respective public repositories where logicmonitor host/push images.
# LogicMonitor Collector

## Overview
Docker image capable of installing and running a LogicMonitor collector

## Website
http://www.logicmonitor.com

## Docker repository
https://hub.docker.com/r/logicmonitor/collector/

## Requirements
- You must have a LogicMonitor account
- The specified token Access Id and Access Key must have sufficient permission to perform the requested actions

## Parameters
All listed parameters are specified as container environment variables at
runtime.

### account:
##### description:
LogicMonitor account name
##### required:
true
##### default:
null

### access_id:
##### description:
LogicMonitor API Token Access ID
##### required:
true
##### default:
null

### access_key:
##### description:
LogicMonitor API Token Access Key
##### required:
true
##### default:
null

### backup_collector_id:
##### description:
The Id of the failover Collector configured for this Collector
##### required:
false
##### default:
null

### cleanup:
##### description:
Whether or not to remove itself from the portal when the container is stopped
##### required:
false
##### default:
False
##### type:
bool

### collector_group:
##### description:
The Id of the group the Collector is in

If a Collector with the same description already exists, use that Collector Id
##### required:
false
##### default:
/

### collector_size:
##### description:
The size of the Collector to install:
- nano requires < 2GB memory
- small requires 2GB memory
- medium requires 4GB memory
- large requires 8GB memory
- extra_large requires 16GB memory (This size is available for EA version only and not for GD and MGD)
- double_extra_large requires 32GB memory (This size is available for EA version only and not for GD and MGD)

##### required:
false
##### default:
small
##### choices:
- nano
- small
- medium
- large
- extra_large
- double_extra_large


### collector_version:
##### description:
The version of the collector to install (without periods or other characters)
https://www.logicmonitor.com/support/settings/collectors/collector-versions/
##### required:
false
##### default:
null

### description:
##### description:
The Collector's description
##### required:
false
##### default:
null

### enable_fail_back:
##### description:
Whether or not automatic failback is enabled for the Collector
##### required:
false
##### default:
False
##### type:
bool

### escalating_chain_id:
##### description:
The Id of the escalation chain associated with this Collector
##### required:
false
##### default:
1

### collector_id:
##### description:
The Id of an existing Collector provision

The specified Collector Id must already exist in order to use this option
##### required:
false
##### default:
null

### resend_interval:
##### description:
The interval, in minutes, after which alert notifications for the Collector will be resent
##### required:
false
##### default:
15

### suppress_alert_clear:
##### description:
Whether alert clear notifications are suppressed for the Collector
##### required:
false
##### default:
False
##### type:
bool

### use_ea:
##### description:
If true, the latest EA Collector version will be used
##### required:
false
##### default:
False
##### type:
bool

### proxy_url:
##### description:
The url of the proxy server
##### required:
false
##### default:
null

### proxy_user:
##### description:
username to authenticate to proxy server
##### required:
false
##### default:
null

### proxy_pass:
##### description:
password to authenticate to proxy server
##### required:
false
##### default:
null

### ignore_ssl:
##### description:
Set flag to ignore ssl/tls validation
##### required:
false
##### default:
false

## Examples
### Creating a new collector
```
docker run --name lm-collector -d \
  -e account=<your portal name> \
  -e access_id=<your api access id> \
  -e access_key=<your api access key> \
  -e backup_collector_id=15 \
  -e collector_group=DockerCollectors \
  -e collector_size=large \
  -e description='My Dockerized Collector' \
  -e enable_fail_back=yes \
  -e escalating_chain_id=1 \
  -e resend_interval=60 \
  -e suppress_alert_clear=no \
  -e cleanup=true \
  -e proxy_url=<your proxy url> \
  -e proxy_user=<your proxy user> \
  -e proxy_pass=<your proxy password> \
logicmonitor/collector:latest
```
### Installing an existing collector
```
docker run --name lm-collector -d \
  -e account=<your portal name> \
  -e access_id=<your api access id> \
  -e access_key=<your api access key> \
  -e collector_id=16 \
  -e collector_size=large \
  -e proxy_url=<your proxy url> \
  -e proxy_user=<your proxy user> \
  -e proxy_pass=<your proxy password> \
logicmonitor/collector:latest
```
