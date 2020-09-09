from typing import Optional

from jsonier.adapter import Adapter
from jsonier.marshalling import require_jsonified, from_json, to_json
from jsonier.util.typespec import type_name


class ObjectAdapter(Adapter):
    def __init__(self, child: type):
        super().__init__()
        require_jsonified(child)
        self._child = child

    def from_json(self, json_data: Optional[dict]):
        if json_data is None:
            return None
        if not isinstance(json_data, dict):
            raise TypeError(f'Expecting a dict, got {type_name(json_data)} instead')
        return from_json(self._child, json_data)

    def to_json(self, obj: Optional[dict]):
        if obj is None:
            return None
        if not isinstance(obj, self._child):
            raise TypeError(f'Expecting a {self._child.__name__}, got {type_name(obj)} instead')
        return to_json(obj)

    def set_default(self, default):
        if default is None:
            self.default = None
        else:
            self.default = self._child(default)