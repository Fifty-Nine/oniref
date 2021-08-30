import os
from typing import Union

import polib


def load_strings(path: Union[str, os.PathLike]):
    po = polib.pofile(str(path))

    result = {}
    for entry in po:
        result[entry.msgctxt] = entry.msgid

    return result
