from logicmonitor_core.Collector import Collector
import os


def main():
    # validate credentials exist
    if ("company" in os.environ and
        "username" in os.environ and
        "password" in os.environ):
            # parse parameters
            params = {}
            params["company"] = os.environ["company"]
            params["user"] = os.environ["username"]
            params["password"] = os.environ["password"]
            params["description"] = ""
            if "description" in os.environ:
                params["description"] = os.environ["description"]

            # create collector object
            col = Collector(params)

            # detect whether collector already exists
            if os.path.isdir("/usr/local/logicmonitor/agent"):
                # start collector
                exit_code = col.start()
            else:
                # create collector
                exit_code = col.create()
    else:
        print("Please specify company, username, and password")
        exit_code = 1

    return exit_code

exit(main())
