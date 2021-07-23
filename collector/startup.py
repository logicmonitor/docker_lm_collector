import collector
import config
import kubernetes
import logging
import os
import param
import sys
import util


def startup(client, params):
    if not params['kubernetes'] and not params['collector_id'] and not params['description']:
        err = '"collector_id" or "description" must be set in non kubernetes environments.'
        util.fail(err)
    c = None

    # if the kubernetes param is specified, assume this is part of a
    # collector set and parse the id accordingly, bypassing other id lookups
    if params['kubernetes']:
        logging.debug('Kubernetes mode enabled. Parsing id from environment')
        collector_id = kubernetes.get_collector_id()
        logging.debug('Parsed id ' + str(collector_id))
        params['collector_id'] = collector_id

    # detect if the collector already exists in the portal
    f = collector.find_collector(client, params)
    if not f:
        logging.debug('Collector not found')
        if params['kubernetes']:
            err = 'Running in kubernetes mode but existing collector not found'
            util.fail(err)
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
