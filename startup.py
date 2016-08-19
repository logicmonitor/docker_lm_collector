from logicmonitor_core.Collector import Collector
import logging
import os
import select
import signal
import socket
import subprocess
import sys
import time

logfile = "/usr/local/logicmonitor/agent/logs/wrapper.log"


def getParams():
    # parse parameters
    params = {}
    params["company"] = os.environ["company"]
    params["user"] = os.environ["username"]
    params["password"] = os.environ["password"]
    params["collector_id"] = ""
    if "collector_id" in os.environ:
        params["collector_id"] = os.environ["collector_id"]
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


# live tail a file
def tail(filename):
    f = subprocess.Popen(["tail", "-F", filename],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p = select.poll()
    p.register(f.stdout)

    while True:
        if p.poll(1):
            sys.stdout.write(f.stdout.readline())
        time.sleep(1)


# gracefully catch and handle docker stop
def signal_term_handler(signal, frame):
    logging.debug("SIGTERM caught.")
    # DON'T DELETE EXISTING COLLECTOR IF COLLECTOR_ID SPECIFIED
    if (
        "collector_id" not in os.environ and
        "cleanup" in os.environ and
        os.environ["cleanup"] is not "False" and
        os.environ["cleanup"] is not "false"
    ):
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
