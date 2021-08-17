import urllib3
from urllib3.util import url

import config
import logging
import logicmonitor_sdk as lm_sdk
import os
import re
import shutil
import subprocess
from subprocess import Popen
import sys
import signal


def fail(err):
    logging.error(err)
    sys.exit(1)


def default_sigpipe():
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)


# execute a local shell command
#   takes an array of arguments and optionally custom current working directory
#   returns dict of {'code': return code, 'stdout': stdout, 'stderr': stderr}
def shell(cmd, cwd=None):
    logging.debug('Running command ' + ' '.join(cmd))
    result = {}
    result['code'] = -1
    result['stdout'] = ''
    result['stderr'] = ''

    try:
        p = (Popen(cmd,
                   stdout=subprocess.PIPE,
                   stderr=subprocess.PIPE,
                   preexec_fn=default_sigpipe,
                   cwd=cwd)
             )
        stdout, stderr = p.communicate()
        result['code'] = p.returncode
        result['stdout'] = stdout or ''
        result['stderr'] = stderr or ''

    except:
        result['code'] = -1
        result['stderr'] = 'Shell execution error'
    return result


def touch(path):
    try:
        with open(path, 'a'):
            os.utime(path, None)
    except:
        return False
    return True


def remove_path(path):
    logging.debug('Removing ' + path)
    if os.path.isfile(path):
        try:
            os.remove(path)
        except:
            logging.debug('Error deleting ' + path)
    if os.path.isdir(path):
        try:
            shutil.rmtree(path)
        except:
            logging.debug('Error deleting ' + path)


# cleanup any leftover lock files
def cleanup():
    logging.debug('Cleaning any existing lock files.')
    if os.path.isdir(config.LOCK_PATH):
        for f in os.listdir(config.LOCK_PATH):
            if re.search('.*\.lck', f):
                remove_path(os.path.join(config.LOCK_PATH, f))
            elif re.search('.*\.pid', f):
                remove_path(os.path.join(config.LOCK_PATH, f))


def get_client(params):
    # Configure API key authorization: LMv1
    conf = lm_sdk.configuration.Configuration()
    conf.company = params['account']
    conf.access_id = params['access_id']
    conf.access_key = params['access_key']
    conf.temp_folder_path = config.TEMP_PATH
    if params['ignore_ssl']:
        conf.verify_ssl = False

    # setting proxy
    proxy = parse_proxy(params)
    proxy_auth = None
    if proxy is not None:
        proxy_url = proxy["netloc"]
        proxy_auth = proxy["auth"]
        conf.proxy = proxy_url
        logging.debug('Using proxy: ' + proxy_url)

    # create an instance of the API class
    api_client = lm_sdk.ApiClient(configuration=conf)

    # The configuration does not support setting proxy_headers, we only set it after creating the api client
    # TODO: if we upgrade SDK in the future, we can consider letting configuration support proxy_headers setting
    if proxy_auth is not None and proxy_auth != '':
        proxy_headers = urllib3.make_headers(proxy_basic_auth=proxy_auth)
        api_client.rest_client.pool_manager.proxy_headers = proxy_headers
        api_client.rest_client.pool_manager.connection_pool_kw['_proxy_headers'] = proxy_headers
    return lm_sdk.LMApi(api_client)


def parse_proxy(params):
    proxy_url = params['proxy_url']
    if proxy_url is None or proxy_url == '':
        return None
    parse_result = url.parse_url(proxy_url)
    scheme = parse_result.scheme or 'http'
    host = parse_result.hostname
    port = parse_result.port
    user = params['proxy_user']
    password = params['proxy_pass']
    auth = None
    host_addr = host

    if user is not None and user != '':
        auth = str(user)
        if password is not None and password != '':
            auth += ':' + str(password)

    if port is not None:
        host_addr += ':' + str(port)
    return {'scheme': scheme,
            'host': host,
            'port': port,
            'user': user,
            'pass': password,
            'auth': auth,
            'host_addr': host_addr,
            'netloc': '%s://%s' % (scheme, host_addr)}