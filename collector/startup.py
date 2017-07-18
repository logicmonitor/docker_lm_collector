import collector
import config
import logging
import os
import param
import sys
import util


def startup(client, c, params):
    # detect whether collector already exists
    if os.path.isdir(config.INSTALL_PATH + config.AGENT_DIRECTORY):
        logging.debug('Collector already installed.')
        logging.debug('Cleaning any existing lock files.')
        util.cleanup()
        return
    else:
        # see if the collector already exists
        f = collector.find_collector(client, params)
        if not f:
            # if not using an existing collector, create one
            c = collector.create_collector(client, c)
        else:
            c = f
            # don't clean up found collectors
            util.touch(config.COLLECTOR_LOCK)
        collector.install_collector(client, c, params)
        return


def main():
    logging.basicConfig(level=logging.DEBUG)
    params = param.parse_params()
    client = util.get_client(params)
    c = collector.collector(client, params)
    startup(client, c, params)
    sys.exit(0)


main()
