import config
import os
import util


def parse_params():
    # parse parameters
    params = {}
    errors = []

    for param, meta in config.PARAM_OPTS.items():
        params[param], success, err = parse_param(param, meta)
        if not success:
            errors.append(err)

    # check for errors
    if len(errors) > 0:
        util.fail(',\n'.join(errors))
    return params


# parse parameter from the environment
#  returns: param_value, success, error
def parse_param(param, meta):
    value = None
    # check if the param has been set in env
    if param in os.environ:
        value = os.environ[param]
    else:
        # check for missing required parameters
        if meta['required'] is True:
            return None, False, 'The parameter ' + param + ' is required'

        # use the default value if param not set
        if 'default' in meta:
            value = meta['default']

    # validate parameters values for type and choice options
    if 'type' in meta:
        return parse_type(value, meta, param)

    if not check_choices(value, meta):
        return None, False, (
                'Value for ' + param + ' must be one of ' +
                ','.join(meta['choices'])
        )
    return value, True, None


#  returns: param_value, success, error
def parse_type(value, meta, param):
    if value is None:
        return value, True, None

    if meta['type'] == 'int':
        return parse_int(value, param)

    if meta['type'] == 'bool':
        return parse_bool(value, param)


def parse_int(value, param):
    success = True
    err = None
    try:
        value = int(value)
    except:
        success = False
        err = 'Value for ' + param + ' must be of type int'
    return value, success, err


def parse_bool(value, param):
    success = True
    err = None

    true = ['true', '1', 'True', 'yes', 'Yes']
    false = ['false', '0', 'False', 'no', 'No']
    bools = [True, False]

    if value not in true and value not in false and value not in bools:
        success = False
        accepted_values = ' or '.join(true + false)
        err = 'Value for ' + param + ' should be ' + accepted_values
        print(value)

    if value in true:
        value = True
    else:
        value = False

    return value, success, err


def check_choices(value, meta):
    if 'choices' in meta and value not in meta['choices']:
        return False
    return True
