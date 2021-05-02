def get_aslist(param):
    return (
        param.get('schema', None) and
        param['schema']['type'] in ['array', 'object']
    )


def get_style(param):
    if 'style' in param:
        return param['style']

    # determine default
    return (
        'simple' if param['in'] in ['path', 'header'] else 'form'
    )


def get_explode(param):
    if 'explode' in param:
        return param['explode']

    # determine default
    style = get_style(param)
    return style == 'form'
