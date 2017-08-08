import config
import logging
import logicmonitor_sdk as lm_sdk
from logicmonitor_sdk.rest import ApiException
import os
import socket
import sys
import util


def collector(client, params):
    obj = None
    kwargs = {
        'enable_fail_back': params['enable_fail_back'],
        'escalating_chain_id': params['escalation_chain_id'],
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
    logging.debug('adding collector')

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
    logging.debug('deleting collector ' + str(collector.id))
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
    logging.debug('finding collector ' + str(id))

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

    logging.debug('finding collector ' + str(params['description']))

    collectors = None
    try:
        collectors = client.get_collector_list(size=-1)
    except ApiException as e:
        err = 'Exception when calling get_collector_list: ' + str(e) + '\n'
        util.fail(err)

    if collectors.status != 200:
        err = (
            'Error ' + str(collectors.status) +
            ' calling get_device_list: ' + str(e) + '\n'
        )
        util.fail(err)

    if 'description' in params and params['description']:
        for item in collectors.data.items:
            if item.description == params['description']:
                return item
    return None


def find_collector_group_id(client, collector_group_name):
    logging.debug('finding collector group ' + str(collector_group_name))

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
            ' calling get_collector_group_list: ' + str(e) + '\n'
        )
        util.fail(err)

    # look for matching collector group
    for item in collector_groups.data.items:
        if item.name == collector_group_name:
            return item.id
    return None


def download_installer(client, collector, params):
    logging.debug('downloading collector ' + str(collector.id))

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
    try:
        resp = client.install_collector(
            str(collector.id),
            os_and_arch,
            **kwargs
        )
    except ApiException as e:
        err = 'Exception when calling install_collector: ' + str(e) + '\n'
        util.fail(err)

    return resp


def install_collector(client, collector, params):
    fail = False
    installer = download_installer(client, collector, params)

    # ensure installer is executable
    os.chmod(installer, 0755)

    logging.debug('installing ' + str(installer))
    result = util.shell([str(installer), ' -y'])

    if result['code'] != 0 or result['stderr'] != '':
        logging.debug(result['stdout'])
        err = result['stderr']
        # if we failed but there's no stderr, set err msg to stdout
        if err == '':
            err = result['stdout']
        fail = True

    # be nice and clean up
    logging.debug('Cleaning up downloaded installer')
    util.remove_path(installer)

    if fail:
        logging.debug('Collector install failed')
        logging.debug('Cleaning up collector install directory')
        util.remove_path(config.INSTALL_PATH + config.AGENT_DIRECTORY)
        util.fail(err)
