import json


def class2json(obj):
    return json.dumps(class2dict(obj), sort_keys=True, indent=4, separators=(',', ': '))


def class2dict(obj):
    params = {}
    for name in dir(obj):
        value = getattr(obj, name)
        if not name.startswith('__') and not callable(value):
            params[name] = value
    return params


def dataframe2dict(df):
    return df.to_dict(orient='records')