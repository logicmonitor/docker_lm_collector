import collector
import config
import logging
import os
import param
import sys
import util


def main():
    logging.basicConfig(level=logging.DEBUG)
    logging.debug('Shutting down')
    params = param.parse_params()
    # DON'T DELETE EXISTING COLLECTOR IF COLLECTOR_ID SPECIFIED
    if (
        not os.path.isfile(config.COLLECTOR_LOCK) and
        'cleanup' in params and
        params['cleanup']
    ):
        client = util.get_client(params)
        c = collector.find_collector(client, params)
        if c:
            logging.debug('Uninstalling collector.')
            # remove the collector
            collector.delete_collector(client, c)

    logging.debug('Shutdown complete.')
    sys.exit(0)


main()
