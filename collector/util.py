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
    lm_sdk.configuration.host = lm_sdk.configuration.host.replace(
        'localhost',
        params['account'] + '.logicmonitor.com'
    )
    lm_sdk.configuration.api_key['id'] = params['access_id']
    lm_sdk.configuration.api_key['Authorization'] = params['access_key']
    lm_sdk.configuration.temp_folder_path = config.TEMP_PATH

    # create an instance of the API class
    return lm_sdk.DefaultApi(lm_sdk.ApiClient())
