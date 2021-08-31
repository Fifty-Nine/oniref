import os
from typing import Dict, Optional, Union

from bs4 import BeautifulSoup as BS
import polib


def strip_tags(text):
    return ''.join(i.get_text() for i in BS(text, 'lxml'))


class KleiStrings:
    def __init__(self, strings: Dict[str, str]):
        self._raw = strings
        self._stripped: Dict[str, str] = {}

    def __len__(self):
        return len(self._raw)

    def _strip(self, key):
        result = self._stripped.get(key)
        if result is None:
            raw = self._raw[key]
            result = self._stripped[key] = strip_tags(raw)

        return result

    def __getitem__(self, key: str):
        return self._strip(key)

    def __iter__(self):
        yield from self._raw

    def get(self, key: str, default: Optional[str] = None):
        try:
            return self[key]
        except KeyError:
            return default

    def keys(self):
        yield from self._raw

    def values(self):
        for key in self._raw:
            yield self._strip(key)

    def items(self):
        yield from zip(self.keys(), self.values())

    def get_raw(self, key, default=None):
        return self._raw.get(key, default)


def load_strings(path: Union[str, os.PathLike]) -> KleiStrings:
    po = polib.pofile(str(path))

    result = {}
    for entry in po:
        result[entry.msgctxt] = entry.msgid

    return KleiStrings(result)
