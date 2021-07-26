import gzip
import re
import tempfile

import config
import logging
import logicmonitor_sdk as lm_sdk
from logicmonitor_sdk.rest import ApiException
import os
import socket
import sys
import util
import json

# TODO this var and the logic that depends on it can be removed after non-root
# installer makes it to MGD
MIN_NONROOT_INSTALL_VER = 28300


def collector(client, params):
    obj = None
    kwargs = {
        'enable_fail_back': params['enable_fail_back'],
        'escalating_chain_id': params['escalating_chain_id'],
        'need_auto_create_collector_device': False
    }

    if 'backup_collector_id' in params and params['backup_collector_id']:
        kwargs['backup_agent_id'] = params['backup_collector_id']
    if 'description' in params and params['description']:
        kwargs['description'] = params['description']
    else:
        kwargs['description'] = socket.getfqdn()
    if 'collector_id' in params and params['collector_id']:
        kwargs['collector_id'] = params['collector_id']
    if 'resend_interval' in params and params['resend_interval']:
        kwargs['resend_ival'] = params['resend_interval']
    if 'suppress_alert_clear' in params and params['suppress_alert_clear']:
        kwargs['suppress_alert_clear'] = params['suppress_alert_clear']
    collector_group = find_collector_group_id(
        client,
        params['collector_group']
    )
    if collector_group is not None:
        kwargs['collector_group_id'] = collector_group
    else:
        err = (
                'Collector group ' + params['collector_group'] +
                ' does not exist.'
        )
        util.fail(err)
    try:
        obj = lm_sdk.Collector(**kwargs)
        return obj
    except Exception as e:
        err = 'Exception creating object: ' + str(e) + '\n'
        util.fail(err)


def create_collector(client, collector):
    logging.debug('Adding collector')
    response = None
    try:
        response = client.add_collector(collector)
    except ApiException as e:
        resp = json.loads(e.body)
        if e.status == 600:
            # Status 600: The record already exists
            return collector
        err = (
                'Exception when calling add_collector: ' + str(e) + '\n'
                                                                    'Status ' + str(e.status) + ' Error Message ' + str(
            resp['errorMessage'])
        )
        util.fail(err)
    return response


def delete_collector(client, collector):
    logging.debug('Deleting collector ' + str(collector.id))
    response = None
    try:
        response = client.delete_collector_by_id(str(collector.id))
    except ApiException as e:
        err = 'Exception when calling delete_collector_by_id: ' + str(e) + '\n'
        util.fail(err)
    if response.status != 200:
        err = (
                'Status ' + str(response.status) +
                ' calling delete_collector_by_id\n' +
                str(response.errmsg)
        )
        util.fail(err)
    return response


def find_collector(client, params):
    if 'collector_id' in params and params['collector_id']:
        return find_collector_by_id(client, params['collector_id'])
    else:
        return find_collector_by_description(client, params)


def find_collector_by_id(client, id):
    logging.debug('Finding collector ' + str(id))
    collector = None
    try:
        collector = client.get_collector_by_id(str(id))
    except ApiException as e:
        resp = json.loads(e.body)
        if e.status == 1404:
            # Status 1404: No such agent
            return None
        err = (
                'Exception when calling get_collector_by_id: ' + str(e) + '\n'
                                                                          'Status ' + str(
            e.status) + ' Error Message ' + str(resp['errorMessage'])
        )
        util.fail(err)
    return collector


def find_collector_by_description(client, params):
    if 'description' not in params or not params['description']:
        return None

    logging.debug('Finding collector ' + str(params['description']))

    collectors = None
    try:
        collectors = client.get_collector_list(size=-1)
    except ApiException as e:
        resp = json.loads(e.body)
        if e.status != 200:
            err = (
                    'Exception when calling get_collector_list: ' + str(e) + '\n'
                                                                             'Status ' + str(
                e.status) + ' Error Message ' + str(resp['errorMessage'])
            )
            util.fail(err)
    if 'description' in params and params['description']:
        for item in collectors.items:
            if item.description == params['description']:
                return item
    return None


def find_collector_group_id(client, collector_group_name):
    logging.debug('Finding collector group ' + str(collector_group_name))

    # if the root group is set, no need to search
    if collector_group_name == '/':
        return 1

    # trim leading / if it exists
    collector_group_name = collector_group_name.lstrip('/')

    collector_groups = None
    try:
        collector_groups = client.get_collector_group_list(size=-1)
    except ApiException as e:
        resp = json.loads(e.body)
        if e.status != 200:
            err = (
                    'Exception when calling get_collector_group_list: ' + str(e) + '\n'
                                                                                   'Status ' + str(
                e.status) + ' Error Message ' + str(resp['errorMessage'])
            )
            util.fail(err)
    # look for matching collector group
    for item in collector_groups.items:
        if item.name == collector_group_name:
            return item.id
    return None


def download_installer(client, collector, params):
    logging.debug('Downloading collector ' + str(collector.id))

    os_and_arch = None
    if sys.maxsize > 2 ** 32:
        os_and_arch = config.DEFAULT_OS + '64'
    else:
        os_and_arch = config.DEFAULT_OS + '32'

    kwargs = {
        'collector_size': params['collector_size'],
        'use_ea': params['use_ea']
    }
    if not kwargs['use_ea']:
        if 'extra_large' in kwargs['collector_size'] or 'double_extra_large' in kwargs['collector_size']:
            err = 'Cannot proceed with installation because only Early Access collector versions support ' + kwargs[
                'collector_size'] + 'size. To proceed further with installation, set \"use_ea\" parameter to true or use appropriate collector size.\n'
            util.fail(err)

    if 'collector_version' in params and params['collector_version']:
        kwargs['collector_version'] = params['collector_version']
    # if the collector already exists and has a version, download that version
    elif collector.build != 0 and not kwargs['use_ea']:
        kwargs['collector_version'] = collector.build
    try:
        response = client.get_collector_installer(
            str(collector.id),
            os_and_arch,
            **kwargs
        )
    except ApiException as e:
        err = 'exception when calling get_collector_installer: ' + str(e) + '\n'
        # check if download failed because of outdated version
        error_message = str(e.body)
        if "only those versions" in error_message.lower():
            err = (
                    error_message +
                    ' Most likely the collector_version ' +
                    str(kwargs['collector_version']) + ' is invalid/out-dated. See ' +
                    'https://www.logicmonitor.com/support/settings/collectors/collector-versions/ ' +
                    'for more information on collector versioning.'
            )
            logging.debug(err)
            return None, "version error"

        util.fail(str(err))
        return
    fd, path = tempfile.mkstemp(dir=client.api_client.configuration.temp_folder_path)
    content_disposition = response.getheader("Content-Disposition")
    if content_disposition:
        filename = re.search(r'filename=[\'"]?([^\'"\s]+)[\'"]?',
                             content_disposition).group(1)
        path = os.path.join(os.path.dirname(path), filename)
    else:
        filename = "logicmonitorsetupx64_" + str(collector.id) + ".bin"
        path = os.path.join(client.api_client.configuration.temp_folder_path, filename)
        logging.warning("Could not form filename using response headers")

    with open(path, "wb") as f:
        f.write(response.data)

    # detect cases where we download an invalid installer
    statinfo = os.stat(path)

    logging.debug("Download successful - size - %s" % (str(statinfo.st_size)))
    return path, None


def install_collector(client, collector, params):
    fail = False
    current_version = collector.build
    installer, err = download_installer(client, collector, params)
    if not installer and err == 'version error':
        # get the latest stable release if not force require EA version;
        collector.build = params['collector_version'] = 0
        log_msg = 'retry to get latest available collector version'
        logging.debug(log_msg)
        installer, err = download_installer(client, collector, params)
        if not installer:
            util.fail(err)

    # ensure installer is executable
    os.chmod(installer, 0o755)

    install_cmd = [
        str(installer), '-y'
    ]

    # force update the collector object to ensure all details are up to date
    # e.g. build version
    if collector.build != 0:
        collector = find_collector_by_id(client, collector.id)
        logging.debug('Collector version ' + str(collector.build))

    # if this is a newer installer that defaults to non-root user, force root
    if int(collector.build) >= MIN_NONROOT_INSTALL_VER or params['use_ea'] or int(collector.build == 0):
        install_cmd.extend(['-u', 'root'])

    proxy = util.parse_proxy(params)
    if proxy is not None:
        proxy_addr = proxy['host_addr']
        proxy_user = proxy['user']
        proxy_pass = proxy['pass']
        install_cmd.extend(['-p', proxy_addr])
        if proxy_user is not None and proxy_user != '':
            install_cmd.extend(['-U', proxy_user])
            if proxy_pass is not None and proxy_pass != '':
                install_cmd.extend(['-P', proxy_pass])

    result = util.shell(install_cmd)
    if result['code'] != 0 or result['stderr'] != '':
        err = result['stderr']
        # if we failed but there's no stderr, set err msg to stdout
        if err == '':
            err = result['stdout']

        # check for false fail condition
        success_msg = 'LogicMonitor Collector has been installed successfully'
        if err.lower().strip().strip('\n') == 'unknown option: u' and \
                success_msg.lower() in str(result['stdout']).lower():
            fail = False
        else:
            logging.debug('Collector install failed')
            logging.debug('stdout: ' + str(result['stdout']))
            logging.debug('stderr: ' + str(result['stderr']))
            logging.debug('Cleaning up collector install directory')
            # util.remove_path(config.INSTALL_PATH + config.AGENT_DIRECTORY)
            fail = True
    if params['ignore_ssl']:
        util.shell(['sed', '-i', 's/EnforceLogicMonitorSSL=true/EnforceLogicMonitorSSL=false/g',
                    '/usr/local/logicmonitor/agent/conf/agent.conf'])

    # be nice and clean up
    logging.debug('Cleaning up downloaded installer')
    # util.remove_path(installer)

    if fail:
        util.fail(err)
    else:
        # log message if version is outdated
        try:
            if os.path.isfile(config.INSTALL_STAT_PATH):
                with open(config.INSTALL_STAT_PATH) as install_stat:
                    for line in install_stat:
                        if 'complexInfo=' in line:
                            key, val = line.partition("=")[::2]
                            complexInfo = json.loads(val.strip('\n'))
                            collector_version = complexInfo['collector']['version'].strip()
                            if str(collector_version) != str(current_version):
                                upgrade_msg = 'Requested collector version %s ' \
                                              'is outdated so upgraded to %s' \
                                              ' version '
                                upgrade_msg = upgrade_msg % (str(current_version), str(collector_version))
                                logging.info(upgrade_msg)
        except:
            pass