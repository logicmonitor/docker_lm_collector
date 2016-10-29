from logicmonitor_core.Collector import Collector
import logging
import os
import socket
import sys


def getParams():
    # parse parameters
    params = {}
    params['company'] = os.environ['company']
    params['user'] = os.environ['username']
    params['password'] = os.environ['password']
    if 'collector_id' in os.environ:
        params['collector_id'] = os.environ['collector_id']
    params['description'] = ''
    if 'description' in os.environ:
        params['description'] = os.environ['description']
    else:
        # put this here to set a default description. The portal will default
        # to this on its own, but for the purpose of doing an uninstall, it's
        # best to do it here as well.
        params['description'] = socket.gethostname()
    return params


def main():
    logging.basicConfig(level=logging.DEBUG)
    # DON'T DELETE EXISTING COLLECTOR IF COLLECTOR_ID SPECIFIED
    if (
        'collector_id' not in os.environ and
        'cleanup' in os.environ and
        os.environ['cleanup'] is not 'False' and
        os.environ['cleanup'] is not 'false'
    ):
        logging.debug('Uninstalling collector.')
        # remove the collector
        params = getParams()
        collector = Collector(params)
        collector._unregister()

    logging.debug('Shutdown complete.')
    sys.exit(0)

main()
