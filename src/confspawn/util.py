from functools import reduce


def deep_get(dic: dict, keys: str, default=None):
    # https://stackoverflow.com/a/46890853/13588694
    return reduce(lambda d, key: d.get(key, default) if isinstance(d, dict) else default,
                  keys.split("."), dic)
