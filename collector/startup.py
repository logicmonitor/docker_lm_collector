import collector
import config
import logging
import os
import param
import sys
import util


def startup(client, params):
    c = None

    # detect if the collector already exists in the portal
    f = collector.find_collector(client, params)
    if not f:
        logging.debug('Collector not found')
        c = collector.collector(client, params)
        c = collector.create_collector(client, c)
    else:
        logging.debug('Collector found')
        c = f

        # we want to make a note on the fs that we found an existing collector
        # so that we don't remove it during a future cleanup, but we should
        # only make this note if this is the first time the container is run
        # (otherwise, every subsequent should detect the existing collector
        # that we're going to create below. Not the behavior we want)
        if not os.path.isfile(config.FIRST_RUN):
            util.touch(config.COLLECTOR_FOUND)

    # let subsequent runs know that this isn't the first container run
    util.touch(config.FIRST_RUN)

    # detect if collector is already installed
    if os.path.isdir(config.INSTALL_PATH + config.AGENT_DIRECTORY):
        logging.debug('Collector already installed.')
        util.cleanup()
        return
    collector.install_collector(client, c, params)


def main():
    logging.basicConfig(level=logging.DEBUG)
    params = param.parse_params()
    client = util.get_client(params)
    startup(client, params)
    sys.exit(0)


main()
