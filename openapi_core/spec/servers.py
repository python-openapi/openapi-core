from six import iteritems


def get_server_default_variables(server):
    if 'variables' not in server:
        return {}

    defaults = {}
    variables = server / 'variables'
    for name, variable in iteritems(variables):
        defaults[name] = variable['default']
    return defaults


def get_server_url(server, **variables):
    if not variables:
        variables = get_server_default_variables(server)
    return server['url'].format(**variables)
