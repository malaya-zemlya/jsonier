from jsonier.adapter import Adapter
from jsonier.util.typespec import type_name, TypeSpec


class MapOfAdapter(Adapter):
    def __init__(self, child: Adapter):
        super().__init__()
        self._child = child

    def from_json(self, json_data: dict):
        if not isinstance(json_data, dict):
            raise TypeError(f'Expecting a dict, got {type(json_data)} instead')
        return {k: self._child.from_json(v) for k, v in json_data.items()}

    def to_json(self, obj: dict):
        if not isinstance(obj, dict):
            raise TypeError(f'Expecting a dict, got {type_name(obj)} instead')
        return {k: self._child.to_json(v) for k, v in obj.items()}

    def set_default(self, default):
        if default is None:
            self.default = None
        else:
            self.default = dict(default)


MapOf = TypeSpec(TypeSpec.MapOf)