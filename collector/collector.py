import config
import logging
import logicmonitor_sdk as lm_sdk
from logicmonitor_sdk.rest import ApiException
import os
import socket
import sys
import util

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
            'Collecor group ' + params['collector_group'] +
            ' does not exist.'
        )
        util.fail(err)
    try:
        obj = lm_sdk.RestCollector(**kwargs)
        return obj
    except Exception as e:
        err = 'Exception creating object: ' + str(e) + '\n'
        util.fail(err)


def create_collector(client, collector):
    logging.debug('Adding collector')

    resp = None
    try:
        resp = client.add_collector(collector)
    except ApiException as e:
        err = 'Exception when calling add_collector: ' + str(e) + '\n'
        util.fail(err)

    if resp.status != 200:
        if resp.status == 600:
            # Status 600: The record already exists
            return collector

        err = (
            'Status ' + str(resp.status) + ' calling add_collector\n' +
            str(resp.errmsg)
        )
        util.fail(err)
    return resp.data


def delete_collector(client, collector):
    logging.debug('Deleting collector ' + str(collector.id))
    resp = None
    try:
        resp = client.delete_collector_by_id(str(collector.id))
    except ApiException as e:
        err = (
            'Exception when calling delete_collector_by_id: ' + str(e) +
            '\n'
        )
        util.fail(err)

    if resp.status != 200:
        err = (
            'Status ' + str(resp.status) +
            ' calling delete_collector_by_id\n' +
            str(resp.errmsg)
        )
        util.fail(err)
    return resp.data


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
        err = 'Exception when calling get_collector_by_id: ' + str(e) + '\n'
        util.fail(err)

    if collector.status != 200:
        if collector.status == 1069:
            # Status 1069: No such agent
            return None

        err = (
            'Status ' + str(collector.status) +
            ' calling find_collector_by_id\n' + str(collector.errmsg)
        )
        util.fail(err)
    return collector.data


def find_collector_by_description(client, params):
    if 'description' not in params or not params['description']:
        return None

    logging.debug('Finding collector ' + str(params['description']))

    collectors = None
    try:
        collectors = client.get_collector_list(size=-1)
    except ApiException as e:
        err = 'Exception when calling get_collector_list: ' + str(e) + '\n'
        util.fail(err)

    if collectors.status != 200:
        err = (
            'Error ' + str(collectors.status) +
            ' calling get_collector_list: ' +
            str(collectors.errmsg) + '\n'
        )
        util.fail(err)

    if 'description' in params and params['description']:
        for item in collectors.data.items:
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
        err = (
            'Exception when calling get_collector_group_list: ' + str(e) + '\n'
        )
        util.fail(err)

    if collector_groups.status != 200:
        err = (
            'Error ' + str(collector_groups.status) +
            ' calling get_collector_group_list: ' +
            str(collector_groups.errmsg) + '\n'
        )
        util.fail(err)

    # look for matching collector group
    for item in collector_groups.data.items:
        if item.name == collector_group_name:
            return item.id
    return None


def download_installer(client, collector, params):
    logging.debug('Downloading collector ' + str(collector.id))

    os_and_arch = None
    if sys.maxsize > 2**32:
        os_and_arch = config.DEFAULT_OS + '64'
    else:
        os_and_arch = config.DEFAULT_OS + '32'

    resp = None
    kwargs = {
        'collector_size': params['collector_size'],
        'use_ea': params['use_ea']
    }
    if 'collector_version' in params and params['collector_version']:
        kwargs['collector_version'] = params['collector_version']
    # if the collector already exists and has a version, download that version
    elif collector.build != 0 and not kwargs['use_ea']:
        kwargs['collector_version'] = collector.build
    try:
        resp = client.install_collector(
            str(collector.id),
            os_and_arch,
            **kwargs
        )
    except ApiException as e:
        err = 'exception when calling install_collector: ' + str(e) + '\n'
        util.fail(err)

    # detect cases where we download an invalid installer
    statinfo = os.stat(resp)
    if statinfo.st_size < 1000:
        err = (
            'Downloaded collector installer is ' +
            str(statinfo.st_size) + ' bytes. This indicates an issue with ' +
            'the download process. Most likely the collector_version ' +
            'is invalid. See ' +
            'https://www.logicmonitor.com/support/settings/collectors/collector-versions/ ' +
            'for more information on collector versioning.'
        )
        util.fail(err)
    return resp


def install_collector(client, collector, params):
    fail = False
    installer = download_installer(client, collector, params)

    # ensure installer is executable
    os.chmod(installer, 0755)

    install_cmd = [
        str(installer), '-y'
    ]

    # force update the collector object to ensure all details are up to date
    # e.g. build version
    collector = find_collector_by_id(client, collector.id)

    # if this is a newer installer that defaults to non-root user, force root
    logging.debug('Collector version ' + str(collector.build))
    if int(collector.build) >= MIN_NONROOT_INSTALL_VER or params['use_ea']:
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

        logging.debug('Collector install failed')
        logging.debug('stdout: ' + str(result['stdout']))
        logging.debug('stderr: ' + str(result['stderr']))
        logging.debug('Cleaning up collector install directory')
        # util.remove_path(config.INSTALL_PATH + config.AGENT_DIRECTORY)
        fail = True

    # be nice and clean up
    logging.debug('Cleaning up downloaded installer')
    # util.remove_path(installer)

    if fail:
        util.fail(err)
