import re
from re import Match
from typing import Dict, Optional, AnyStr, Callable


def replace(m: Match, replace_dict: Dict[AnyStr, AnyStr]):
    return replace_dict[m.group(1)]


def sub_template(template_str, replace_dict: Optional[Dict[AnyStr, AnyStr]] = None,
                 repl: Optional[Callable[[Match], AnyStr]] = None):
    # Matches `~spawn@` literally, then any character except line breaks `(.*?)` lazily
    # Finally matches @~ literally. The first capture group is everything between the two `@`.
    # So use match.group(1).
    if repl is None:
        def replace_fn(m: Match):
            return replace(m, replace_dict)
    else:
        replace_fn = repl

    return re.sub(r"~spwn@(.*?)@~", replace_fn, template_str)
