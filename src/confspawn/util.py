from functools import reduce


def _get_upper_or_lower(dic: dict, key: str, default):
    got = dic.get(key)
    if got is None:
        if key.isupper():
            got = dic.get(key.lower())
        elif key.islower():
            got = dic.get(key.upper())
    return got if got is not None else default


def deep_get(dic: dict, keys: str, default=None):
    # https://stackoverflow.com/a/46890853/13588694
    return reduce(lambda d, key: _get_upper_or_lower(d, key, default) if isinstance(d, dict) else default,
                  keys.split("."), dic)
