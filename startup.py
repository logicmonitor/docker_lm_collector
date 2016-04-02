from logicmonitor_core.Collector import Collector
import os
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
    return params


def startup(params):
    # create collector object
    collector = Collector(params)

    # detect whether collector already exists
    if os.path.isdir("/usr/local/logicmonitor/agent"):
        # start collector
        collector.start()
    else:
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
    if "cleanup" in os.environ:
        # remove the collector
        params = getParams()
        collector = Collector(params)
        sys.exit(collector.remove())
    else:
        sys.exit(0)

signal.signal(signal.SIGTERM, signal_term_handler)


def main():
    # validate credentials exist
    if ("company" in os.environ and
        "username" in os.environ and
        "password" in os.environ):

        params = getParams()

        # start and install collector
        startup(params)

        # tail log file.
        # No need to check success. Program will exit if above command fails
        tail(logfile)

    else:
        print("Please specify company, username, and password")
        sys.exit(1)

main()
