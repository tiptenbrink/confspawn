from typing import List, Union

import re


def search_dict(d: Union[dict, list], parent=None):
    keys = []
    if isinstance(d, dict):
        for key in d.keys():
            if parent is None:
                parent = []
            append_key = [*parent, key]
            keys.append(append_key)
            sub_d = d[key]
            if isinstance(sub_d, dict):
                keys += search_dict(sub_d, parent=append_key)
            if isinstance(sub_d, list):
                keys += search_dict(sub_d, parent=append_key)
    elif isinstance(d, list):
        for i, val in enumerate(d):
            if parent is None:
                parent = []
            append_key = [*parent, i]
            keys.append(append_key)
            if isinstance(val, dict):
                keys += search_dict(val, parent=append_key)
            if isinstance(val, list):
                keys += search_dict(val, parent=append_key)
    return keys


def key_find(all_keys: List):
    var_keys = []
    for key_path in all_keys:
        # < .. > match those exact character
        # ( .. ) match capture group
        # .*? match every character 0 or more times lazily
        key = key_path[-1]
        # print(key)
        # print(re.search(r"<(.*?)>", key))
        re_match = re.search(r"<(.*?)>", str(key))
        if re_match:
            # group 0 is the whole match
            # group 1 is the first parenthesized match
            print(re_match.group(1))
            print(key_path)
            var_keys.append((re_match.group(1), key_path))
    return var_keys


def deep_get(d: dict, path, parent_d=None):
    if len(path) > 0:
        key = path.pop(0)
        return deep_get(d[key], path, d)
    else:
        return d, parent_d


def replace(template: dict, source, var_keys):
    var_keys.sort(key=lambda v: len(v[-1]))
    var_keys = list(reversed(var_keys))

    modified_conf = template.copy()
    for var_key, key_path in var_keys:
        sub_d, d = deep_get(modified_conf, key_path.copy())
        new_key = source.get(var_key)
        d[new_key] = sub_d
        del d[key_path[-1]]

    return modified_conf


def template_replace(template: dict, source):
    all_keys = search_dict(template)
    var_keys = key_find(all_keys)
    modified_conf = replace(template, source, var_keys)
    return modified_conf
