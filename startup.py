import logging
from logicmonitor_core.Collector import Collector
import os
import socket
import signal
import sys
import time

logfile = "/usr/local/logicmonitor/agent/logs/wrapper.log"


def getParams():
    # parse parameters
    params = {}
    params["company"] = os.environ["company"]
    params["user"] = os.environ["username"]
    params["password"] = os.environ["password"]
    params["description"] = ""
    if "description" in os.environ:
        params["description"] = os.environ["description"]
    else:
        # put this here to set a default description. The portal will default
        # to this on its own, but for the purpose of doing an uninstall, it's
        # best to do it here as well.
        params["description"] = socket.gethostname()
    return params


def startup(params):
    # create collector object
    collector = Collector(params)

    # detect whether collector already exists
    if os.path.isdir("/usr/local/logicmonitor/agent"):
        logging.debug("Collector already installed. Starting.")
        # start collector
        collector.start()
    else:
        logging.debug("Installing collector.")
        # create collector
        collector.create()


# https://code.activestate.com/recipes/578424-tailing-a-live-log-file-with-python/
def tail(outfile):
    with open(outfile, 'rt') as following:
        following.seek(-64, 2)
        for line in follow(following):
            sys.stdout.write(line)


def follow(stream):
    # Follow the live contents of a text file
    line = ''
    for block in iter(lambda: stream.read(1024), None):
        if '\n' in block:
            # Only enter this block if we have at least one line to yield.
            # The +[''] part is to catch the corner case of when a block
            # ends in a newline, in which case it would repeat a line.
            for line in (line+block).splitlines(True)+['']:
                if line.endswith('\n'):
                    yield line
            # When exiting the for loop, 'line' has any remaninig text.
        elif not block:
            # Wait for data.
            time.sleep(1.0)


# gracefully catch and handle docker stop
def signal_term_handler(signal, frame):
    logging.debug("SIGTERM caught.")
    if ("cleanup" in os.environ and
       os.environ["cleanup"] is not "False" and
       os.environ["cleanup"] is not "false"):
            logging.debug("Uninstalling collector.")
            # remove the collector
            params = getParams()
            collector = Collector(params)
            sys.exit(collector.remove())
    else:
        logging.debug("Exiting.")
        sys.exit(0)


def main():
    # validate credentials exist
    if ("company" in os.environ and
        "username" in os.environ and
       "password" in os.environ):
            # install and/or start collector
            params = getParams()
            startup(params)

            # tail log file if successful
            tail(logfile)

    else:
        print("Please specify company, username, and password")
        sys.exit(1)

# TERM handler
signal.signal(signal.SIGTERM, signal_term_handler)
main()
