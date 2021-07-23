import os
import socket
import util


def get_set_index():
    hostname = socket.gethostname().split('-')
    if len(hostname) < 1:
        err = 'Unable to parse set index from hostname\n'
        util.fail(err)
    return hostname[-1]


def get_collector_id_list_from_env():
    collector_ids = os.getenv('COLLECTOR_IDS')
    if not collector_ids:
        err = 'Environment variable COLLECTOR_IDS not set\n'
        util.fail(err)
    collector_ids = collector_ids.split(',')
    if len(collector_ids) < 1:
        err = 'Unable to parse ids from COLLECTOR_IDS\n'
        util.fail(err)
    return collector_ids


def get_collector_id():
    set_index = get_set_index()
    collector_ids = get_collector_id_list_from_env()
    set_index = parse_id(set_index)

    if len(collector_ids) < set_index + 1:
        err = (
                'Set index ' + str(set_index) +
                ' is greater than number of collector ids ' +
                str(len(collector_ids)) + '\n'
        )
        util.fail(err)
    return collector_ids[set_index]


def parse_id(value):
    try:
        return int(value)
    except Exception as e:
        err = 'Unable to parse set index ' + str(e) + '\n'
        util.fail(err)
